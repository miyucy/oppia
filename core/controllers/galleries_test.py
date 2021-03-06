# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the gallery pages."""

__author__ = 'Sean Lip'

from core.controllers import galleries
from core.domain import config_services
from core.domain import exp_services
from core.domain import rights_manager
from core.tests import test_utils
import feconf

CAN_EDIT_STR = 'can_edit'


class LearnGalleryTest(test_utils.GenericTestBase):

    EDITOR_EMAIL = 'editor@example.com'
    USER_EMAIL = 'user@example.com'

    def test_learn_gallery_page(self):
        """Test access to the learners' gallery page."""
        response = self.testapp.get(feconf.LEARN_GALLERY_URL)
        self.assertEqual(response.status_int, 200)
        response.mustcontain(
            'Gallery', 'Categories',
            # Test that no edit/copy links are shown (at least in the HTML
            # template; a full test should check what happens after the JS is
            # loaded and data is fetched from the backend).
            no=[CAN_EDIT_STR, 'Create New Exploration']
        )

        # Test that the correct navbar tab is active.
        self.assertRegexpMatches(
            response.body, r'class="active">\s+<a href="/learn">Learn')

    def test_learn_gallery_handler(self):
        """Test access to the learners' gallery data handler."""
        # Load a demo exploration. This is only in beta so it does not show
        # up in the learners' gallery.
        exp_services.load_demo('0')

        response_dict = self.get_json(feconf.LEARN_GALLERY_DATA_URL)
        self.assertEqual({
            'is_admin': False,
            'is_moderator': False,
            'is_super_admin': False,
            'categories': {}
        }, response_dict)

    def test_login_message(self):
        """Test that the login message appears when appropriate."""
        response = self.testapp.get(feconf.LEARN_GALLERY_URL)
        self.assertEqual(response.status_int, 200)
        response.mustcontain(
            'To create new explorations or edit existing ones, you must',
            self.get_expected_login_url(feconf.CONTRIBUTE_GALLERY_URL),
            no=['To create new explorations or edit existing ones, visit the'])

        self.login(self.USER_EMAIL)
        response = self.testapp.get(feconf.LEARN_GALLERY_URL)
        self.assertEqual(response.status_int, 200)
        response.mustcontain(
            'To create new explorations or edit existing ones, visit the',
            no=['To create new explorations or edit existing ones, you must',
                self.get_expected_login_url(feconf.CONTRIBUTE_GALLERY_URL)])
        self.logout()

    def test_new_exploration_ids(self):
        """Test generation of exploration ids."""
        self.register_editor(self.EDITOR_EMAIL)
        self.login(self.EDITOR_EMAIL)

        response = self.testapp.get(feconf.CONTRIBUTE_GALLERY_URL)
        self.assertEqual(response.status_int, 200)
        csrf_token = self.get_csrf_token_from_response(response)
        EXP_A_DICT = {'title': 'A', 'category': 'Test Explorations'}
        exp_a_id = self.post_json(
            feconf.NEW_EXPLORATION_URL, EXP_A_DICT, csrf_token
        )[galleries.EXPLORATION_ID_KEY]
        self.assertEqual(len(exp_a_id), 12)


class PlaytestQueueTest(test_utils.GenericTestBase):

    EDITOR_EMAIL = 'editor@example.com'
    PLAYTESTER_A_EMAIL = 'pa@example.com'
    PLAYTESTER_B_EMAIL = 'pb@example.com'

    def test_playtest_queue_page(self):
        """Test access to the playtesters' queue page."""
        response = self.testapp.get(feconf.PLAYTEST_QUEUE_URL)
        self.assertEqual(response.status_int, 200)
        response.mustcontain(
            'Playtesters\' Queue',
            # Test that no edit/copy links are shown (at least in the HTML
            # template; a full test should check what happens after the JS is
            # loaded and data is fetched from the backend).
            no=[CAN_EDIT_STR, 'Create New Exploration', 'Categories']
        )

        # Test that the correct navbar tab is active.
        self.assertRegexpMatches(
            response.body, r'class="active">\s+<a href="/playtest">Playtest')

    def test_playtest_queue_handler(self):
        """Test access to the playtesters' queue data handler."""
        # Load a demo exploration, which ends up being in beta.
        exp_services.load_demo('0')

        response_dict = self.get_json(feconf.PLAYTEST_QUEUE_DATA_URL)
        self.assertDictContainsSubset({
            'is_admin': False,
            'is_moderator': False,
            'is_super_admin': False,
            'private_explorations_list': [],
        }, response_dict)
        self.assertIn('public_explorations_list', response_dict)
        self.assertEqual(len(response_dict['public_explorations_list']), 1)
        self.assertDictContainsSubset({
            'category': 'Welcome',
            'id': '0',
            'title': 'Welcome to Oppia!',
            'to_playtest': False
        }, response_dict['public_explorations_list'][0])
        self.assertIn(
            'last_updated', response_dict['public_explorations_list'][0])

    def test_can_see_explorations_to_playtest(self):
        """Test viewability of playtestable explorations."""
        # E registers and logs in as an editor.
        self.register_editor(self.EDITOR_EMAIL)
        self.login(self.EDITOR_EMAIL)

        # E creates new explorations A and B.
        response = self.testapp.get(feconf.CONTRIBUTE_GALLERY_URL)
        self.assertEqual(response.status_int, 200)
        csrf_token = self.get_csrf_token_from_response(response)
        EXP_A_DICT = {'title': 'A', 'category': 'Test Explorations'}
        EXP_B_DICT = {'title': 'B', 'category': 'Test Explorations'}
        exp_a_id = self.post_json(
            feconf.NEW_EXPLORATION_URL, EXP_A_DICT, csrf_token
        )[galleries.EXPLORATION_ID_KEY]
        exp_b_id = self.post_json(
            feconf.NEW_EXPLORATION_URL, EXP_B_DICT, csrf_token
        )[galleries.EXPLORATION_ID_KEY]

        # E allows PA to playtest exploration A, and allows PB to playtest
        # exploration B.
        response = self.testapp.get(
            '%s/%s' % (feconf.EDITOR_URL_PREFIX, exp_a_id))
        self.assertEqual(response.status_int, 200)
        csrf_token = self.get_csrf_token_from_response(response)
        self.put_json(
            '%s/%s' % (feconf.EXPLORATION_RIGHTS_PREFIX, exp_a_id), {
                'version': 1,
                'new_member_email': self.PLAYTESTER_A_EMAIL,
                'new_member_role': rights_manager.ROLE_VIEWER
            }, csrf_token)
        self.put_json(
            '%s/%s' % (feconf.EXPLORATION_RIGHTS_PREFIX, exp_b_id), {
                'version': 1,
                'new_member_email': self.PLAYTESTER_B_EMAIL,
                'new_member_role': rights_manager.ROLE_VIEWER
            }, csrf_token)

        # E logs out.
        self.logout()

        # An anonymous user sees nothing to playtest on the Playtest page.
        response_dict = self.get_json(feconf.PLAYTEST_QUEUE_DATA_URL)
        self.assertEqual({
            'is_admin': False,
            'is_moderator': False,
            'is_super_admin': False,
            'public_explorations_list': [],
            'private_explorations_list': [],
        }, response_dict)

        # If PA logs in, he sees exploration A but not exploration B on the
        # Learn page.
        self.login(self.PLAYTESTER_A_EMAIL)
        response_dict = self.get_json(feconf.PLAYTEST_QUEUE_DATA_URL)
        self.assertEqual(len(response_dict['public_explorations_list']), 0)
        self.assertEqual(len(response_dict['private_explorations_list']), 1)
        self.assertDictContainsSubset({
            'category': 'Test Explorations',
            'id': exp_a_id,
            'title': 'A',
            'to_playtest': True
        }, response_dict['private_explorations_list'][0])
        self.logout()

        # E does not see either exploration on the Playtest page.
        self.login(self.EDITOR_EMAIL)
        response_dict = self.get_json(feconf.PLAYTEST_QUEUE_DATA_URL)
        self.assertDictContainsSubset({
            'is_admin': False,
            'is_moderator': False,
            'is_super_admin': False,
            'public_explorations_list': [],
            'private_explorations_list': [],
        }, response_dict)
        self.logout()


class ContributeGalleryTest(test_utils.GenericTestBase):

    def test_contribute_gallery_page(self):
        """Test access to the contributors' gallery page."""
        # If the user is not logged in, redirect to a login page.
        response = self.testapp.get(feconf.CONTRIBUTE_GALLERY_URL)
        self.assertEqual(response.status_int, 302)
        self.assertEqual(
            response.location,
            self.get_expected_login_url(feconf.CONTRIBUTE_GALLERY_URL))

        # The user is logged in, but has not registered. Redirect to the
        # editor prerequisites page.
        self.login('editor@example.com')
        response = self.testapp.get(feconf.CONTRIBUTE_GALLERY_URL)
        self.assertEqual(response.status_int, 302)
        self.assertIn(
            feconf.EDITOR_PREREQUISITES_URL, response.headers['location'])
        response = response.follow()
        self.assertEqual(response.status_int, 200)
        response.mustcontain(
            'Welcome to the Oppia contributor community!',
            'My preferred Oppia username')
        self.logout()

        # The user registers as an editor, and can now see the contributors'
        # gallery.
        self.register_editor('editor@example.com')
        self.login('editor@example.com')
        response = self.testapp.get(feconf.CONTRIBUTE_GALLERY_URL)
        self.assertEqual(response.status_int, 200)
        response.mustcontain('Create New Exploration', CAN_EDIT_STR)
        # Test that the correct navbar tab is active.
        self.assertRegexpMatches(
            response.body,
            r'class="active">\s+<a href="/contribute">Contribute')
        self.logout()

    def test_contribute_gallery_handler(self):
        """Test the contribute gallery data handler."""

        # If the user is not logged in, redirect to a login page.
        response = self.testapp.get(feconf.CONTRIBUTE_GALLERY_URL)
        self.assertEqual(response.status_int, 302)
        self.assertEqual(
            response.location,
            self.get_expected_login_url(feconf.CONTRIBUTE_GALLERY_URL))

        # The user is logged in, but has not registered. Redirect to the editor
        # prerequisites page.
        self.login('editor@example.com')
        response = self.testapp.get(feconf.CONTRIBUTE_GALLERY_URL)
        self.assertEqual(response.status_int, 302)
        self.assertIn(
            feconf.EDITOR_PREREQUISITES_URL, response.headers['location'])
        response = response.follow()
        self.assertEqual(response.status_int, 200)
        response.mustcontain(
            'Welcome to the Oppia contributor community!',
            'My preferred Oppia username')
        self.logout()

        # The user registers as an editor, and can now access the contributors'
        # gallery data handler.
        self.register_editor('editor@example.com')
        self.login('editor@example.com')
        response_dict = self.get_json(feconf.CONTRIBUTE_GALLERY_DATA_URL)
        # Users may not edit the sample exploration for the splash page.
        self.assertDictContainsSubset({
            'is_admin': False,
            'is_super_admin': False,
            'categories': {}
        }, response_dict)
        self.logout()

    def test_exploration_upload_button(self):
        """Test that the exploration upload button appears when appropriate."""
        self.register_editor('editor@example.com')
        self.login('editor@example.com')

        response = self.testapp.get(feconf.CONTRIBUTE_GALLERY_URL)
        self.assertEqual(response.status_int, 200)
        response.mustcontain(no=['Upload Existing Exploration'])

        config_services.set_property(
            feconf.ADMIN_COMMITTER_ID, 'allow_yaml_file_upload', True)

        response = self.testapp.get(feconf.CONTRIBUTE_GALLERY_URL)
        self.assertEqual(response.status_int, 200)
        response.mustcontain('Upload Existing Exploration')

        self.logout()


class ContributeGalleryRightsTest(test_utils.GenericTestBase):

    EMAIL_A = 'a@example.com'
    EMAIL_B = 'b@example.com'
    EMAIL_C = 'c@example.com'
    EMAIL_USER = 'user@example.com'
    EMAIL_MODERATOR = 'moderator@example.com'
    EMAIL_ADMIN = 'admin@example.com'
    EMAIL_SUPERADMIN = 'superadmin@example.com'

    # These are initialized during the test setup.
    exp_a_id = None
    exp_b_id = None
    exp_c_id = None

    def setUp(self):
        """Create three explorations, an admin, and a moderator.

        Exploration A is owned by a@example.com and is private.
        Exploration B is owned by b@example.com and is public but not
            community-editable.
        Exploration C is owned by c@example.com and is public and is
            community-editable.

        The person with email address moderator@example.com is a
        moderator. The person with email address admin@example.com is
        an admin.
        """
        super(ContributeGalleryRightsTest, self).setUp()

        self.register_editor(self.EMAIL_A, username='a')
        self.register_editor(self.EMAIL_B, username='b')
        self.register_editor(self.EMAIL_C, username='c')
        self.register_editor(self.EMAIL_MODERATOR, username='moderator')
        self.register_editor(self.EMAIL_ADMIN, username='adm')

        self.login(self.EMAIL_A)
        response = self.testapp.get(feconf.CONTRIBUTE_GALLERY_URL)
        csrf_token = self.get_csrf_token_from_response(response)
        EXP_A_DICT = {'title': 'A', 'category': 'Test Explorations'}
        self.exp_a_id = self.post_json(
            feconf.NEW_EXPLORATION_URL, EXP_A_DICT, csrf_token
        )[galleries.EXPLORATION_ID_KEY]
        self.logout()

        self.login(self.EMAIL_B)
        response = self.testapp.get(feconf.CONTRIBUTE_GALLERY_URL)
        csrf_token = self.get_csrf_token_from_response(response)
        EXP_B_DICT = {'title': 'B', 'category': 'Test Explorations'}
        self.exp_b_id = self.post_json(
            feconf.NEW_EXPLORATION_URL, EXP_B_DICT, csrf_token
        )[galleries.EXPLORATION_ID_KEY]

        response = self.testapp.get(
            '%s/%s' % (feconf.EDITOR_URL_PREFIX, self.exp_b_id))
        csrf_token = self.get_csrf_token_from_response(response)
        # Do the minimal change needed to make the exploration valid.
        exp_dict = self.get_json(
            '%s/%s' % (feconf.EXPLORATION_DATA_PREFIX, self.exp_b_id))
        init_state_name = exp_dict['init_state_name']
        widget_handlers = exp_dict['states'][
            init_state_name]['widget']['handlers']
        widget_handlers[0]['rule_specs'][0]['dest'] = 'END'
        self.put_json(
            '%s/%s' % (feconf.EXPLORATION_DATA_PREFIX, self.exp_b_id),
            {
                'version': 1,
                'commit_message': 'Make exploration valid',
                'change_list': [{
                    'cmd': 'edit_state_property',
                    'state_name': exp_dict['init_state_name'],
                    'property_name': 'widget_handlers',
                    'new_value': {'submit': widget_handlers[0]['rule_specs']},
                }, {
                    'cmd': 'edit_exploration_property',
                    'property_name': 'objective',
                    'new_value': 'An objective',
                }]
            },
            csrf_token
        )
        # Change the exploration status to public.
        self.put_json(
            '%s/%s' % (feconf.EXPLORATION_RIGHTS_PREFIX, self.exp_b_id),
            {'is_public': True, 'version': 2},
            csrf_token
        )
        self.logout()

        self.login(self.EMAIL_C)
        response = self.testapp.get(feconf.CONTRIBUTE_GALLERY_URL)
        csrf_token = self.get_csrf_token_from_response(response)
        EXP_C_DICT = {'title': 'C', 'category': 'Test Explorations'}
        self.exp_c_id = self.post_json(
            feconf.NEW_EXPLORATION_URL, EXP_C_DICT, csrf_token
        )[galleries.EXPLORATION_ID_KEY]

        response = self.testapp.get(
            '%s/%s' % (feconf.EDITOR_URL_PREFIX, self.exp_c_id))
        csrf_token = self.get_csrf_token_from_response(response)
        # Do the minimal change needed to make the exploration valid.
        exp_dict = self.get_json(
            '%s/%s' % (feconf.EXPLORATION_DATA_PREFIX, self.exp_c_id))
        init_state_name = exp_dict['init_state_name']
        widget_handlers = exp_dict['states'][
            init_state_name]['widget']['handlers']
        widget_handlers[0]['rule_specs'][0]['dest'] = 'END'
        self.put_json(
            '%s/%s' % (feconf.EXPLORATION_DATA_PREFIX, self.exp_c_id),
            {
                'version': 1,
                'commit_message': 'Make exploration valid',
                'change_list': [{
                    'cmd': 'edit_state_property',
                    'state_name': exp_dict['init_state_name'],
                    'property_name': 'widget_handlers',
                    'new_value': {'submit': widget_handlers[0]['rule_specs']},
                }, {
                    'cmd': 'edit_exploration_property',
                    'property_name': 'objective',
                    'new_value': 'An objective',
                }]
            },
            csrf_token
        )
        # Change the exploration status to public and community-editable.
        self.put_json(
            '%s/%s' % (feconf.EXPLORATION_RIGHTS_PREFIX, self.exp_c_id),
            {'is_public': True, 'version': 2},
            csrf_token
        )
        self.put_json(
            '%s/%s' % (feconf.EXPLORATION_RIGHTS_PREFIX, self.exp_c_id),
            {'is_community_owned': True, 'version': 2},
            csrf_token
        )
        self.logout()

        # Now create a moderator and admin.
        self.set_moderators([self.EMAIL_MODERATOR])
        self.set_admins([self.EMAIL_ADMIN])

    def attempt_to_view(self, exploration_id, expect_errors=False, version=1):
        if expect_errors:
            expected_status_int = 404
        else:
            expected_status_int = 200

        response = self.testapp.get(
            '%s/%s' % (feconf.EDITOR_URL_PREFIX, exploration_id),
            expect_errors=expect_errors)
        self.assertEqual(response.status_int, expected_status_int)

    def attempt_to_edit(self, exploration_id, expect_errors=False, version=1):
        # This should only be called if attempt_to_view() passes, otherwise
        # it isn't possible to get a CSRF token.
        response = self.testapp.get(
            '%s/%s' % (feconf.EDITOR_URL_PREFIX, exploration_id))
        self.assertEqual(response.status_int, 200)
        csrf_token = self.get_csrf_token_from_response(response)

        if expect_errors:
            expected_status_int = 401
        else:
            expected_status_int = 200

        self.put_json(
            '%s/%s' % (feconf.EXPLORATION_DATA_PREFIX, exploration_id),
            {
                'version': version,
                'commit_message': 'change category',
                'change_list': [{
                    'cmd': 'edit_exploration_property',
                    'property_name': 'category',
                    'new_value': 'New Category',
                    'old_value': 'Test Explorations'
                }]
            },
            csrf_token=csrf_token, expect_errors=expect_errors,
            expected_status_int=expected_status_int)

    def attempt_to_delete(self, exploration_id, expect_errors=False):
        if expect_errors:
            expected_status_int = 401
        else:
            expected_status_int = 200

        response = self.testapp.delete(
            '%s/%s' % (feconf.EXPLORATION_DATA_PREFIX, str(exploration_id)),
            expect_errors=expect_errors
        )
        self.assertEqual(response.status_int, expected_status_int)

    def test_user_rights(self):
        """Test user rights for explorations in the Contribute gallery."""

        # user@example.com, a regular user, can see exploration B, can see and
        # edit exploration C, and cannot delete any of the explorations.
        self.register_editor(self.EMAIL_USER)

        self.login(self.EMAIL_USER)
        response_dict = self.get_json(feconf.CONTRIBUTE_GALLERY_DATA_URL)

        self.assertDictContainsSubset({
            'is_admin': False,
            'is_super_admin': False,
        }, response_dict)
        self.assertEqual(sorted([{
            'can_edit': False,
            'title': 'B',
            'id': self.exp_b_id,
            'is_private': False,
            'is_cloned': False,
            'is_public': True,
            'is_publicized': False,
            'is_community_owned': False,
        }, {
            'can_edit': True,
            'title': 'C',
            'id': self.exp_c_id,
            'is_private': False,
            'is_cloned': False,
            'is_public': True,
            'is_publicized': False,
            'is_community_owned': True,
        }]), sorted(response_dict['categories']['Test Explorations']))

        self.attempt_to_view(self.exp_a_id, expect_errors=True, version=2)
        self.attempt_to_delete(self.exp_a_id, expect_errors=True)

        self.attempt_to_view(self.exp_b_id, version=2)
        self.attempt_to_edit(self.exp_b_id, expect_errors=True, version=2)
        self.attempt_to_delete(self.exp_b_id, expect_errors=True)

        self.attempt_to_view(self.exp_c_id, version=2)
        self.attempt_to_edit(self.exp_c_id, version=2)
        self.attempt_to_delete(self.exp_c_id, expect_errors=True)

        self.logout()

    def test_moderator_rights(self):
        """Test moderator rights for explorations in the Contribute gallery."""

        # The moderator can see, edit and delete both Explorations B and C.
        self.login(self.EMAIL_MODERATOR)
        response_dict = self.get_json(feconf.CONTRIBUTE_GALLERY_DATA_URL)
        self.assertDictContainsSubset({
            'is_admin': False,
            'is_super_admin': False,
        }, response_dict)
        self.assertEqual(sorted([{
            'can_edit': True,
            'title': 'B',
            'id': self.exp_b_id,
            'is_private': False,
            'is_cloned': False,
            'is_public': True,
            'is_publicized': False,
            'is_community_owned': False,
        }, {
            'can_edit': True,
            'title': 'C',
            'id': self.exp_c_id,
            'is_private': False,
            'is_cloned': False,
            'is_public': True,
            'is_publicized': False,
            'is_community_owned': True,
        }]), sorted(response_dict['categories']['Test Explorations']))

        self.attempt_to_view(self.exp_a_id, version=2)
        self.attempt_to_edit(self.exp_a_id, expect_errors=True)
        self.attempt_to_delete(self.exp_a_id, expect_errors=True)

        self.attempt_to_view(self.exp_b_id, version=2)
        self.attempt_to_edit(self.exp_b_id, version=2)
        self.attempt_to_delete(self.exp_b_id)

        self.attempt_to_view(self.exp_c_id, version=2)
        self.attempt_to_edit(self.exp_c_id, version=2)
        self.attempt_to_delete(self.exp_c_id)

        self.logout()

    def test_admin_rights(self):
        """Test admin rights for explorations in the Contribute gallery."""

        # The admin can see, edit and delete both Explorations B and C.
        self.login(self.EMAIL_ADMIN)
        response_dict = self.get_json(feconf.CONTRIBUTE_GALLERY_DATA_URL)
        self.assertDictContainsSubset({
            'is_admin': True,
            'is_super_admin': False,
        }, response_dict)
        self.assertEqual(sorted([{
            'can_edit': True,
            'title': 'B',
            'id': self.exp_b_id,
            'is_private': False,
            'is_cloned': False,
            'is_public': True,
            'is_publicized': False,
            'is_community_owned': False,
        }, {
            'can_edit': True,
            'title': 'C',
            'id': self.exp_c_id,
            'is_private': False,
            'is_cloned': False,
            'is_public': True,
            'is_publicized': False,
            'is_community_owned': True,
        }]), sorted(response_dict['categories']['Test Explorations']))

        self.attempt_to_view(self.exp_a_id, version=2)
        self.attempt_to_edit(self.exp_a_id, expect_errors=True)
        self.attempt_to_delete(self.exp_a_id, expect_errors=True)

        self.attempt_to_view(self.exp_b_id, version=2)
        self.attempt_to_edit(self.exp_b_id, version=2)
        self.attempt_to_delete(self.exp_b_id)

        self.attempt_to_view(self.exp_c_id, version=2)
        self.attempt_to_edit(self.exp_c_id, version=2)
        self.attempt_to_delete(self.exp_c_id)

        self.logout()

    def test_superadmin_rights(self):
        """Test super-admin rights in the Contribute gallery."""

        # superadmin@example.com, a super admin, has no special rights and is
        # equivalent to a user.
        self.register_editor(self.EMAIL_SUPERADMIN)

        self.login(self.EMAIL_SUPERADMIN, is_super_admin=True)
        response_dict = self.get_json(feconf.CONTRIBUTE_GALLERY_DATA_URL)
        self.assertDictContainsSubset({
            'is_admin': False,
            'is_super_admin': True,
        }, response_dict)
        self.assertEqual(sorted([{
            'can_edit': False,
            'title': 'B',
            'id': self.exp_b_id,
            'is_private': False,
            'is_cloned': False,
            'is_public': True,
            'is_publicized': False,
            'is_community_owned': False,
        }, {
            'can_edit': True,
            'title': 'C',
            'id': self.exp_c_id,
            'is_private': False,
            'is_cloned': False,
            'is_public': True,
            'is_publicized': False,
            'is_community_owned': True,
        }]), sorted(response_dict['categories']['Test Explorations']))

        self.attempt_to_view(self.exp_a_id, expect_errors=True, version=2)
        self.attempt_to_delete(self.exp_a_id, expect_errors=True)

        self.attempt_to_view(self.exp_b_id, version=2)
        self.attempt_to_edit(self.exp_b_id, expect_errors=True)
        self.attempt_to_delete(self.exp_b_id, expect_errors=True)

        self.attempt_to_view(self.exp_c_id, version=2)
        self.attempt_to_edit(self.exp_c_id, version=2)
        self.attempt_to_delete(self.exp_c_id, expect_errors=True)

        self.logout()
