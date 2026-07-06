from care.emr.resources.scheduling.schedule.spec import SchedulableResourceTypeOptions
from care.users.models import User

from care_notifications.recipients.healthcare_service import managing_org_members
from care_notifications.recipients.location import location_org_members


def booking_resource_recipients(resource):
    """Users to alert for a booking, chosen by the slot's schedulable resource:
    - practitioner -> the practitioner
    - healthcare_service -> members of the service's managing organization
    - location -> members of the location's organizations
    """
    if resource is None:
        return User.objects.none()

    if resource.resource_type == SchedulableResourceTypeOptions.practitioner.value:
        if resource.user_id is None:
            return User.objects.none()
        return User.objects.filter(id=resource.user_id)

    if resource.resource_type == SchedulableResourceTypeOptions.healthcare_service.value:
        return managing_org_members(resource.healthcare_service)

    if resource.resource_type == SchedulableResourceTypeOptions.location.value:
        return location_org_members(resource.location)

    return User.objects.none()
