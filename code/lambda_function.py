import boto3
import datetime
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ce = boto3.client('ce')
sns = boto3.client('sns')
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    try:
        today = datetime.datetime.utcnow().date()
        last_week_start = today - datetime.timedelta(days=7)
        last_week_end = today - datetime.timedelta(days=1)

        weekly_data = get_daily_costs(last_week_start, last_week_end)
        if not weekly_data:
            logger.warning("No cost data for last week.")
            return

        weekly_avg = {svc: total / 7 for svc, total in weekly_data.items()}

        today_data = get_daily_cost(today)
        sorted_today = sorted(today_data.items(), key=lambda x: x[1], reverse=True)

        alerts = []
        for service, cost in sorted_today:
            avg = weekly_avg.get(service, 0)
            if avg > 0 and cost > avg * 1.10:
                alerts.append(
                    f"Service: {service}, Cost: ${cost:.2f} exceeds 10% of weekly avg (${avg:.2f})"
                )

        if alerts:
            msg = "\n".join(alerts)
            send_alert(msg)
            logger.info("Anomaly alert sent.")
        else:
            logger.info("No anomalies detected.")

    except Exception as e:
        logger.error("Unhandled exception", exc_info=True)

def get_daily_costs(start_date, end_date):
    try:
        response = ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.isoformat(),
                'End': (end_date + datetime.timedelta(days=1)).isoformat()
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )

        totals = {}
        for day in response['ResultsByTime']:
            for group in day['Groups']:
                svc = group['Keys'][0]
                amt = float(group['Metrics']['UnblendedCost']['Amount'])
                totals[svc] = totals.get(svc, 0) + amt

        return totals

    except Exception as e:
        logger.error("Failed to fetch weekly cost data", exc_info=True)
        return {}

def get_daily_cost(date):
    try:
        next_day = (date + datetime.timedelta(days=1)).isoformat()
        response = ce.get_cost_and_usage(
            TimePeriod={
                'Start': date.isoformat(),
                'End': next_day
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )

        daily = {}
        for group in response['ResultsByTime'][0]['Groups']:
            svc = group['Keys'][0]
            amt = float(group['Metrics']['UnblendedCost']['Amount'])
            daily[svc] = amt

        return daily

    except Exception as e:
        logger.error("Failed to fetch today’s cost data", exc_info=True)
        return {}

def send_alert(message):
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject='🔔 AWS Cost Alert'
        )
    except Exception as e:
        logger.error("SNS publish failed", exc_info=True)
