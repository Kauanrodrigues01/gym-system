from django.test import TestCase
from django.utils.timezone import localdate
from members.models import Member, Payment
from admin_panel.models import ActivityLog, DailyReport


class TestActivityLog(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = Member.objects.create(
            email='test@member.com', full_name='Test Member', phone='1234567890', is_active=True
        )
        cls.activity_log = ActivityLog.objects.create(
            member=cls.member,
            event_type='created',
            description='Test member created'
        )

    def test_activity_log_creation(self):
        """Verify that an activity log is correctly created and its attributes are accurate."""
        self.assertEqual(self.activity_log.member, self.member)
        self.assertEqual(self.activity_log.event_type, 'created')
        self.assertEqual(self.activity_log.description, 'Test member created')
        self.assertEqual(str(self.activity_log), 'Created - Test member created')

    def test_activity_log_event_type_choices(self):
        """Ensure that activity log accepts valid event types."""
        log_created = ActivityLog.objects.create(
            member=None, event_type='created', description='A member was created'
        )
        self.assertEqual(log_created.event_type, 'created')

        log_updated = ActivityLog.objects.create(
            member=None, event_type='updated', description='A member was updated'
        )
        self.assertEqual(log_updated.event_type, 'updated')

        log_delete = ActivityLog.objects.create(
            member=None, event_type='delete', description='A member was delete'
        )
        self.assertEqual(log_delete.event_type, 'delete')

        log_payment = ActivityLog.objects.create(
            member=None, event_type='payment', description='A member was payment'
        )
        self.assertEqual(log_payment.event_type, 'payment')

    def test_activity_log_str(self):
        """Verify the string representation of an activity log."""
        activity_log = ActivityLog.objects.create(
            member=None,
            event_type='payment',
            description='Payment received'
        )
        self.assertEqual(str(activity_log), 'Payment - Payment received')


class TestDailyReport(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member_active = Member.objects.create(
            email='active@member.com', full_name='Active Member', phone='1234567890', is_active=True
        )
        cls.member_inactive = Member.objects.create(
            email='inactive@member.com', full_name='Inactive Member', phone='0987654321', is_active=False
        )
        cls.payment = Payment.objects.create(
            member=cls.member_active, payment_date=localdate(), amount=100.0
        )

    def test_create_daily_report_success(self):
        """Test successful creation of a daily report with correct values."""
        report = DailyReport.create_report()
        self.assertEqual(report.active_students, 1)
        self.assertEqual(report.pending_students, 1)
        self.assertEqual(report.new_students, 2)
        self.assertEqual(report.daily_profit, 100.0)
        self.assertEqual(report.payments.count(), 1)
        self.assertEqual(report.payments.all()[0], self.payment)

    def test_create_report_with_future_date(self):
        """Ensure that creating a report with a future date raises an error."""
        future_date = localdate().replace(year=localdate().year + 1)
        with self.assertRaises(ValueError):
            DailyReport.create_report(date=future_date)

    def test_create_report_with_invalid_date_type(self):
        """Ensure that an invalid date type raises an error."""
        with self.assertRaises(ValueError):
            DailyReport.create_report(date="Invalid Date")

    def test_create_daily_report_without_date(self):
        """Test daily report creation when no date is provided."""
        report = DailyReport.create_report(date=None)

        self.assertEqual(report.active_students, 1)
        self.assertEqual(report.pending_students, 1)
        self.assertEqual(report.new_students, 2)
        self.assertEqual(report.daily_profit, 100.0)
        self.assertEqual(report.payments.count(), 1)
        self.assertEqual(report.payments.all()[0], self.payment)

    def test_daily_report_str_representation(self):
        """Verify the string representation of a daily report."""
        report = DailyReport.objects.create(
            date=localdate(),
            active_students=5,
            pending_students=2,
            new_students=3,
            daily_profit=150.0
        )
        self.assertEqual(str(report), f"Daily Report for {report.date}")

    def test_daily_report_multiple_payments(self):
        """Ensure the daily report accurately calculates total profit with multiple payments."""
        payment1 = Payment.objects.create(
            member=self.member_active, payment_date=localdate(), amount=50.0
        )
        payment2 = Payment.objects.create(
            member=self.member_active, payment_date=localdate(), amount=70.0
        )

        report = DailyReport.create_report(date=localdate())

        self.assertEqual(report.daily_profit, (payment1.amount + payment2.amount + self.payment.amount))
        self.assertEqual(report.payments.count(), 3)
        list_payments = [self.payment, payment1, payment2]
        self.assertIn(report.payments.all()[0], list_payments)
        self.assertIn(report.payments.all()[1], list_payments)
        self.assertIn(report.payments.all()[2], list_payments)