from core.models import Intent
from core.workflows.actions import create_locked_out_ticket, create_maintenance_ticket, create_rent_info_event, save_action_item


class WorkflowDispatcher:
    def dispatch(self, intent, action_items, email_message, context):
        """
        Map LLM intent → workflow generator.
        """

        if intent == Intent.locked_out:
            ticket = create_locked_out_ticket(context, action_items)
            return save_and_return(ticket)

        if intent == Intent.maintenance:
            ticket = create_maintenance_ticket(context, action_items)
            return save_and_return(ticket)

        if intent == Intent.rent:
            event = create_rent_info_event(context)
            return save_and_return(event)

        # general → no action
        return None


def save_and_return(action):
    path = save_action_item(action)
    return {"saved_to": path, "intent": action['type']}
