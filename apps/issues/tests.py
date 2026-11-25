
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

        self.second_category = Category.objects.create(
            category_name_en="Water Supply",
            category_name_ne="खानेपानी",
            description_en="Water supply problems",
            description_ne="खानेपानी सम्बन्धी समस्या",
            is_active=True,
        )

        self.second_district = District.objects.create(
            district_name="Second Test District"
        )

        self.second_municipality = Municipality.objects.create(
            district=self.second_district,
            municipality_name="Second Test Municipality",
        )

        self.second_ward = Ward.objects.create(
            municipality=self.second_municipality,
            ward_number=2,
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
        self.assertEqual(issue.status, "Submitted")

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

    def test_guest_can_view_issue_list(self):
        Issue.objects.create(
            user=self.user,
            category=self.category,
            ward=self.ward,
            title=self.issue_data["title"],
            description=self.issue_data["description"],
            latitude=self.issue_data["latitude"],
            longitude=self.issue_data["longitude"],
        )

        response = self.client.get(reverse("issue-list"))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)

    def test_guest_can_view_issue_details(self):
        issue = Issue.objects.create(
            user=self.user,
            category=self.category,
            ward=self.ward,
            title=self.issue_data["title"],
            description=self.issue_data["description"],
            latitude=self.issue_data["latitude"],
            longitude=self.issue_data["longitude"],
        )

        response = self.client.get(
            reverse("issue-detail", kwargs={"pk": issue.id})
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(response.data["title"], issue.title)

    def test_nonexistent_issue_returns_404(self):
        response = self.client.get(
            reverse("issue-detail", kwargs={"pk": 9999})
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_filter_issues_by_category(self):
        Issue.objects.create(
            user=self.user,
            category=self.category,
            ward=self.ward,
            title="Road Damage Issue",
            description="Damaged road",
            latitude=27.7172,
            longitude=85.3240,
        )

        Issue.objects.create(
            user=self.user,
            category=self.second_category,
            ward=self.second_ward,
            title="Water Supply Issue",
            description="No water supply",
            latitude=27.7000,
            longitude=85.3000,
        )

        response = self.client.get(
            reverse("issue-list"),
            {"category": self.category.id},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["title"],
            "Road Damage Issue",
        )

    def test_filter_issues_by_district(self):
        Issue.objects.create(
            user=self.user,
            category=self.category,
            ward=self.ward,
            title="First District Issue",
            description="Issue in first district",
            latitude=27.7172,
            longitude=85.3240,
        )

        Issue.objects.create(
            user=self.user,
            category=self.second_category,
            ward=self.second_ward,
            title="Second District Issue",
            description="Issue in second district",
            latitude=27.7000,
            longitude=85.3000,
        )

        response = self.client.get(
            reverse("issue-list"),
            {"district": self.district.id},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["title"],
            "First District Issue",
        )

    def test_filter_issues_by_municipality(self):
        Issue.objects.create(
            user=self.user,
            category=self.category,
            ward=self.ward,
            title="First Municipality Issue",
            description="Issue in first municipality",
            latitude=27.7172,
            longitude=85.3240,
        )

        Issue.objects.create(
            user=self.user,
            category=self.second_category,
            ward=self.second_ward,
            title="Second Municipality Issue",
            description="Issue in second municipality",
            latitude=27.7000,
            longitude=85.3000,
        )

        response = self.client.get(
            reverse("issue-list"),
            {"municipality": self.municipality.id},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["title"],
            "First Municipality Issue",
        )

    def test_filter_issues_by_ward(self):
        Issue.objects.create(
            user=self.user,
            category=self.category,
            ward=self.ward,
            title="Ward 1 Issue",
            description="Issue in ward 1",
            latitude=27.7172,
            longitude=85.3240,
        )

        Issue.objects.create(
            user=self.user,
            category=self.second_category,
            ward=self.second_ward,
            title="Ward 2 Issue",
            description="Issue in ward 2",
            latitude=27.7000,
            longitude=85.3000,
        )

        response = self.client.get(
            reverse("issue-list"),
            {"ward": self.ward.id},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["title"],
            "Ward 1 Issue",
        )

    def test_search_issues_by_title(self):
        Issue.objects.create(
            user=self.user,
            category=self.category,
            ward=self.ward,
            title="Pothole on Main Road",
            description="Damaged road surface",
            latitude=27.7172,
            longitude=85.3240,
        )

        Issue.objects.create(
            user=self.user,
            category=self.second_category,
            ward=self.second_ward,
            title="Water Supply Problem",
            description="No water available",
            latitude=27.7000,
            longitude=85.3000,
        )

        response = self.client.get(
            reverse("issue-list"),
            {"search": "Pothole"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["title"],
            "Pothole on Main Road",
        )

    def test_search_issues_by_description(self):
        Issue.objects.create(
            user=self.user,
            category=self.category,
            ward=self.ward,
            title="Road Problem",
            description="Large pothole near the school",
            latitude=27.7172,
            longitude=85.3240,
        )

        Issue.objects.create(
            user=self.user,
            category=self.second_category,
            ward=self.second_ward,
            title="Water Supply Problem",
            description="No water available",
            latitude=27.7000,
            longitude=85.3000,
        )

        response = self.client.get(
            reverse("issue-list"),
            {"search": "pothole"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["title"],
            "Road Problem",
        )

    def test_search_issues_with_category_filter(self):
        Issue.objects.create(
            user=self.user,
            category=self.category,
            ward=self.ward,
            title="Pothole on Main Road",
            description="Damaged road surface",
            latitude=27.7172,
            longitude=85.3240,
        )

        Issue.objects.create(
            user=self.user,
            category=self.second_category,
            ward=self.second_ward,
            title="Pothole near Water Supply",
            description="Damaged road surface",
            latitude=27.7000,
            longitude=85.3000,
        )

        response = self.client.get(
            reverse("issue-list"),
            {
                "search": "Pothole",
                "category": self.category.id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["title"],
            "Pothole on Main Road",
        )
