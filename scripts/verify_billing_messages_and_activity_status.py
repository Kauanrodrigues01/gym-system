from members.models import Member, BillingMessage
from members.tasks import update_members_activity_status, send_billing_messages

# Testing the update of member activity status
members = Member.objects.all()[:3]  # Selects the first 3 members
print("Before update_members_activity_status:")
for idx, member in enumerate(members, start=1):
    print(f"Member {idx}: ID={member.id}, Name={member.full_name}, is_active={member.is_active}")

# Call the task to update member activity status
update_members_activity_status()

print("\nAfter update_members_activity_status:")
for idx, member in enumerate(members, start=1):
    member.refresh_from_db()  # Refresh data from the database to get the updated status
    print(f"Member {idx}: ID={member.id}, Name={member.full_name}, is_active={member.is_active}")
    if member.is_active != False:  # Check if the member is inactive
        print(f"❌ Error: Member {idx} (ID={member.id}, Name={member.full_name}) should be inactive but is still active.")

# Testing the sending of billing messages
messages = BillingMessage.objects.all()[:3]  # Selects the first 3 billing messages
print("\nBefore send_billing_messages:")
for idx, message in enumerate(messages, start=1):
    member = message.member  # Gets the member associated with the message
    print(f"Message {idx}: ID={message.id}, Member Name={member.full_name}, is_sent={message.is_sent}")

# Call the task to send billing messages
send_billing_messages()

print("\nAfter send_billing_messages:")
for idx, message in enumerate(messages, start=1):
    message.refresh_from_db()  # Refresh data from the database to get the updated status
    member = message.member  # Gets the member associated with the message
    print(f"Message {idx}: ID={message.id}, Member Name={member.full_name}, is_sent={message.is_sent}")
    if message.is_sent != True:  # Check if the message was sent
        print(f"❌ Error: Message {idx} (ID={message.id}, Member Name={member.full_name}) should be sent but is not.")
