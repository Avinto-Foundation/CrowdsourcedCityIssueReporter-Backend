
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
from apps.categories.models import Category
from apps.geography.models import District, Municipality, Ward
from apps.issues.models import Issue


class IssueCreationTests(APITestCase):

    def setUp(self):
        self.registered_role = Role.objects.get(
            role_name="Registered User"
        )

        self.staff_role = Role.objects.get(
            role_name="Municipality Staff"
        )

        self.user = User.objects.create_user(
            username="testissueuser",
            email="testissueuser@example.com",
            password="TestPassword123!",
            full_name="Test Issue User",
            role=self.registered_role,
        )

        self.staff_user = User.objects.create_user(
            username="teststaff",
            email="teststaff@example.com",
            password="TestPassword123!",
            full_name="Test Staff User",
            role=self.staff_role,
        )

        self.category = Category.objects.create(
            category_name_en="Road Damage",
            category_name_ne="सडक क्षति",
            description_en="Damaged roads",
            description_ne="क्षतिग्रस्त सडक",
            is_active=True,
        )

        self.district = District.objects.create(
            district_name="Test District"
        )

        self.municipality = Municipality.objects.create(
            district=self.district,
            municipality_name="Test Municipality",
        )

        self.ward = Ward.objects.create(
            municipality=self.municipality,
            ward_number=1,
        )

        self.url = reverse("issue-create")

        self.issue_data = {
            "category": self.category.id,
            "ward": self.ward.id,
            "title": "Pothole on Main Road",
            "description": "There is a large pothole on the road.",
            "latitude": 27.7172,
            "longitude": 85.3240,
        }

    def test_registered_user_can_create_issue(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            self.issue_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(Issue.objects.count(), 1)

        issue = Issue.objects.first()

        self.assertEqual(issue.user, self.user)
        self.assertEqual(issue.title, self.issue_data["title"])

    def test_guest_cannot_create_issue(self):
        response = self.client.post(
            self.url,
            self.issue_data,
            format="json",
        )

        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ])

        self.assertEqual(Issue.objects.count(), 0)

    def test_municipality_staff_cannot_create_issue(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.post(
            self.url,
            self.issue_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(Issue.objects.count(), 0)

    def test_user_cannot_create_issue_with_inactive_category(self):
        self.client.force_authenticate(user=self.user)

        self.category.is_active = False
        self.category.save()

        response = self.client.post(
            self.url,
            self.issue_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(Issue.objects.count(), 0)

    def test_required_fields_cannot_be_missing(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(Issue.objects.count(), 0)

    def test_invalid_latitude_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        data = self.issue_data.copy()
        data["latitude"] = 100

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(Issue.objects.count(), 0)

    def test_invalid_longitude_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        data = self.issue_data.copy()
        data["longitude"] = 200

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(Issue.objects.count(), 0)

    def test_user_cannot_set_issue_priority(self):
        self.client.force_authenticate(user=self.user)

        data = self.issue_data.copy()
        data["priority"] = "Urgent"

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        issue = Issue.objects.get()

        self.assertEqual(issue.priority, "Medium")
