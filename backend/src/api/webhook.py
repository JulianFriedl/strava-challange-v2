from flask import Blueprint, jsonify, request
import logging

from services.api_services.webhook_service import process_event
from api.exceptions import ParamError

logger = logging.getLogger(__name__)
webhook_blueprint = Blueprint('webhook', __name__)

VERIFY_TOKEN = 'fhgndpahFHDdjdbG837zFH9g98ghH'

@webhook_blueprint.route('', methods=['GET', 'POST'])
def webhook_callback():
    if request.method == 'GET':
        return handle_subscription_verification(request)

    if request.method == 'POST':
        return handle_webhook_event(request)

def handle_subscription_verification(req):
    """Handles the initial subscription verification from Strava."""
    challenge = req.args.get('hub.challenge')
    verify_token = req.args.get('hub.verify_token')
    logger.info(f"Subscription verification received. challenge:{challenge}, verify_token:{verify_token}.")
    if challenge and verify_token == VERIFY_TOKEN:
        logger.info("Subscription verification received.")
        return jsonify({'hub.challenge': challenge}), 200
    else:
        logger.warning("Subscription verification failed.")
        return jsonify({'error': 'Missing challenge parameter'}), 400

def handle_webhook_event(req):
    """Handles incoming webhook events from Strava."""
    event = req.json
    if not event:
        logger.warning("Webhook event received with no JSON payload.")
        return jsonify({'error': 'Invalid payload'}), 400

    try:
        process_event(event)
        logger.info("Webhook event processed successfully.")
        return '', 200
    except ParamError as e:
        logger.error(f"Param error: {str(e)}")
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        logger.error(f"Error processing webhook event: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

