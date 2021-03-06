# coding: utf-8
#
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

__author__ = 'Jeremy Emerson'

from core.domain import event_services
from core.domain import exp_domain
from core.domain import exp_services
from core.domain import rule_domain
from core.domain import stats_domain
from core.domain import stats_services
from core.tests import test_utils
import feconf

# TODO(sfederwisch): Move off of old models. Old models use string
# versions of the rules, while the new ones take in the whole rule.
# This will require moving off of DEFAULT_RULESPEC_STR in those cases.


class AnalyticsEventHandlersUnitTests(test_utils.GenericTestBase):
    """Test the event handlers for analytics events."""

    DEFAULT_RULESPEC_STR = exp_domain.DEFAULT_RULESPEC_STR
    DEFAULT_RULESPEC = exp_domain.RuleSpec.get_default_rule_spec(
        'sid', 'NormalizedString')
    SUBMIT_HANDLER = stats_services.SUBMIT_HANDLER_NAME

    def test_record_state_hit(self):
        event_services.StateHitEventHandler.record('eid', 'sname', True)

        counter = stats_domain.StateCounter.get('eid', 'sname')
        self.assertEquals(counter.first_entry_count, 1)
        self.assertEquals(counter.subsequent_entries_count, 0)
        self.assertEquals(counter.resolved_answer_count, 0)
        self.assertEquals(counter.active_answer_count, 0)
        self.assertEquals(counter.total_entry_count, 1)
        self.assertEquals(counter.no_answer_count, 1)

        answer_log = stats_domain.StateRuleAnswerLog.get(
            'eid', 'sname', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC_STR)
        self.assertEquals(answer_log.answers, {})

        event_services.StateHitEventHandler.record('eid', 'sname', False)

        counter = stats_domain.StateCounter.get('eid', 'sname')
        self.assertEquals(counter.first_entry_count, 1)
        self.assertEquals(counter.subsequent_entries_count, 1)
        self.assertEquals(counter.resolved_answer_count, 0)
        self.assertEquals(counter.active_answer_count, 0)
        self.assertEquals(counter.total_entry_count, 2)
        self.assertEquals(counter.no_answer_count, 2)

        answer_log = stats_domain.StateRuleAnswerLog.get(
            'eid', 'sname', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC_STR)
        self.assertEquals(answer_log.answers, {})

    def test_record_answer_submitted(self):
        event_services.StateHitEventHandler.record('eid', 'sname', True)
        event_services.AnswerSubmissionEventHandler.record(
            'eid', 1, 'sname', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC,
            'answer')

        counter = stats_domain.StateCounter.get('eid', 'sname')
        self.assertEquals(counter.first_entry_count, 1)
        self.assertEquals(counter.subsequent_entries_count, 0)
        self.assertEquals(counter.total_entry_count, 1)
        self.assertEquals(counter.resolved_answer_count, 0)
        self.assertEquals(counter.active_answer_count, 1)
        self.assertEquals(counter.no_answer_count, 0)

        answer_log = stats_domain.StateRuleAnswerLog.get(
            'eid', 'sname', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC_STR)
        self.assertEquals(answer_log.answers, {'answer': 1})

        event_services.StateHitEventHandler.record('eid', 'sname', False)
        event_services.AnswerSubmissionEventHandler.record(
            'eid', 1, 'sname', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC,
            'answer')

        counter = stats_domain.StateCounter.get('eid', 'sname')
        self.assertEquals(counter.first_entry_count, 1)
        self.assertEquals(counter.subsequent_entries_count, 1)
        self.assertEquals(counter.total_entry_count, 2)
        self.assertEquals(counter.resolved_answer_count, 0)
        self.assertEquals(counter.active_answer_count, 2)
        self.assertEquals(counter.no_answer_count, 0)

        answer_log = stats_domain.StateRuleAnswerLog.get(
            'eid', 'sname', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC_STR)
        self.assertEquals(answer_log.answers, {'answer': 2})

        event_services.StateHitEventHandler.record('eid', 'sname', False)

        counter = stats_domain.StateCounter.get('eid', 'sname')
        self.assertEquals(counter.first_entry_count, 1)
        self.assertEquals(counter.subsequent_entries_count, 2)
        self.assertEquals(counter.total_entry_count, 3)
        self.assertEquals(counter.resolved_answer_count, 0)
        self.assertEquals(counter.active_answer_count, 2)
        self.assertEquals(counter.no_answer_count, 1)

        answer_log = stats_domain.StateRuleAnswerLog.get(
            'eid', 'sname', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC_STR)
        self.assertEquals(answer_log.answers, {'answer': 2})

    def test_resolve_answers_for_default_rule(self):
        event_services.StateHitEventHandler.record('eid', 'sname', True)

        # Submit three answers.
        event_services.AnswerSubmissionEventHandler.record(
            'eid', 1, 'sname', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC,
            'a1')
        event_services.AnswerSubmissionEventHandler.record(
            'eid', 1, 'sname', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC,
            'a2')
        event_services.AnswerSubmissionEventHandler.record(
            'eid', 1, 'sname', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC,
            'a3')

        counter = stats_domain.StateCounter.get('eid', 'sname')
        self.assertEquals(counter.resolved_answer_count, 0)
        self.assertEquals(counter.active_answer_count, 3)

        answer_log = stats_domain.StateRuleAnswerLog.get(
            'eid', 'sname', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC_STR)
        self.assertEquals(
            answer_log.answers, {'a1': 1, 'a2': 1, 'a3': 1})

        # Nothing changes if you try to resolve an invalid answer.
        event_services.DefaultRuleAnswerResolutionEventHandler.record(
            'eid', 'sname', self.SUBMIT_HANDLER, ['fake_answer'])
        answer_log = stats_domain.StateRuleAnswerLog.get(
            'eid', 'sname', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC_STR)
        self.assertEquals(
            answer_log.answers, {'a1': 1, 'a2': 1, 'a3': 1})

        # Resolve two answers.
        event_services.DefaultRuleAnswerResolutionEventHandler.record(
            'eid', 'sname', self.SUBMIT_HANDLER, ['a1', 'a2'])

        counter = stats_domain.StateCounter.get('eid', 'sname')
        self.assertEquals(counter.resolved_answer_count, 2)
        self.assertEquals(counter.active_answer_count, 1)

        answer_log = stats_domain.StateRuleAnswerLog.get(
            'eid', 'sname', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC_STR)
        self.assertEquals(answer_log.answers, {'a3': 1})

        # Nothing changes if you try to resolve an answer that has already
        # been resolved.
        event_services.DefaultRuleAnswerResolutionEventHandler.record(
            'eid', 'sname', self.SUBMIT_HANDLER, ['a1'])
        answer_log = stats_domain.StateRuleAnswerLog.get(
            'eid', 'sname', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC_STR)
        self.assertEquals(answer_log.answers, {'a3': 1})

        # Resolve the last answer.
        event_services.DefaultRuleAnswerResolutionEventHandler.record(
            'eid', 'sname', self.SUBMIT_HANDLER, ['a3'])

        counter = stats_domain.StateCounter.get('eid', 'sname')
        self.assertEquals(counter.resolved_answer_count, 3)
        self.assertEquals(counter.active_answer_count, 0)

        answer_log = stats_domain.StateRuleAnswerLog.get(
            'eid', 'sname', self.SUBMIT_HANDLER, 'Rule')
        self.assertEquals(answer_log.answers, {})


class StateImprovementsUnitTests(test_utils.GenericTestBase):
    """Test the get_state_improvements() function."""

    DEFAULT_RULESPEC_STR = exp_domain.DEFAULT_RULESPEC_STR
    DEFAULT_RULESPEC = exp_domain.RuleSpec.get_default_rule_spec(
        'sid', 'NormalizedString')
    SUBMIT_HANDLER = stats_services.SUBMIT_HANDLER_NAME

    def test_get_state_improvements(self):
        exp = exp_domain.Exploration.create_default_exploration(
            'eid', 'A title', 'A category')
        exp_services.save_new_exploration('fake@user.com', exp)

        for _ in range(5):
            event_services.StateHitEventHandler.record(
                'eid', exp.init_state_name, True)

        event_services.AnswerSubmissionEventHandler.record(
            'eid', 1, exp.init_state_name, self.SUBMIT_HANDLER,
            self.DEFAULT_RULESPEC, '1')
        for _ in range(2):
            event_services.AnswerSubmissionEventHandler.record(
                'eid', 1, exp.init_state_name, self.SUBMIT_HANDLER,
                self.DEFAULT_RULESPEC, '2')
        self.assertEquals(stats_services.get_state_improvements('eid'), [{
            'type': 'default',
            'rank': 3,
            'state_name': exp.init_state_name
        }])

    def test_single_default_rule_hit(self):
        exp = exp_domain.Exploration.create_default_exploration(
            'eid', 'A title', 'A category')
        exp_services.save_new_exploration('fake@user.com', exp)
        state_name = exp.init_state_name

        event_services.StateHitEventHandler.record('eid', state_name, True)
        event_services.AnswerSubmissionEventHandler.record(
            'eid', 1, state_name, self.SUBMIT_HANDLER,
            self.DEFAULT_RULESPEC, '1')
        self.assertEquals(stats_services.get_state_improvements('eid'), [{
            'type': 'default',
            'rank': 1,
            'state_name': exp.init_state_name
        }])

    def test_no_improvement_flag_hit(self):
        exp = exp_domain.Exploration.create_default_exploration(
            'eid', 'A title', 'A category')
        exp_services.save_new_exploration('fake@user.com', exp)

        not_default_rule_spec = exp_domain.RuleSpec({
            'rule_type': rule_domain.ATOMIC_RULE_TYPE,
            'name': 'NotDefault',
            'inputs': {},
            'subject': 'answer'
        }, exp.init_state_name, [], [], 'NormalizedString')
        default_rule_spec = exp_domain.RuleSpec.get_default_rule_spec(
            feconf.END_DEST, 'NormalizedString')
        exp.init_state.widget.handlers[0].rule_specs = [
            not_default_rule_spec, default_rule_spec
        ]
        exp_services._save_exploration('fake@user.com', exp, '', [])

        event_services.StateHitEventHandler.record(
            'eid', exp.init_state_name, True)
        event_services.AnswerSubmissionEventHandler.record(
            'eid', 1, exp.init_state_name, self.SUBMIT_HANDLER,
            not_default_rule_spec, '1')
        self.assertEquals(stats_services.get_state_improvements('eid'), [])

    def test_incomplete_and_default_flags(self):
        exp = exp_domain.Exploration.create_default_exploration(
            'eid', 'A title', 'A category')
        exp_services.save_new_exploration('fake@user.com', exp)
        state_name = exp.init_state_name

        # Hit the default rule once, and fail to answer twice. The result
        # should be classified as incomplete.
        for _ in range(3):
            event_services.StateHitEventHandler.record(
                'eid', state_name, True)
        event_services.AnswerSubmissionEventHandler.record(
            'eid', 1, state_name, self.SUBMIT_HANDLER,
            self.DEFAULT_RULESPEC, '1')
        self.assertEquals(stats_services.get_state_improvements('eid'), [{
            'rank': 2,
            'type': 'incomplete',
            'state_name': state_name
        }])

        # Now hit the default two more times. The result should be classified
        # as default.
        for i in range(2):
            event_services.StateHitEventHandler.record(
                'eid', state_name, True)
            event_services.AnswerSubmissionEventHandler.record(
                'eid', 1, state_name, self.SUBMIT_HANDLER,
                self.DEFAULT_RULESPEC, '1')
        self.assertEquals(stats_services.get_state_improvements('eid'), [{
            'rank': 3,
            'type': 'default',
            'state_name': state_name
        }])

    def test_two_state_default_hit(self):
        exp = exp_domain.Exploration.create_default_exploration(
            'eid', 'A title', 'A category')
        exp_services.save_new_exploration('fake@user.com', exp)

        FIRST_STATE_NAME = exp.init_state_name
        SECOND_STATE_NAME = 'State 2'
        exp.add_states([SECOND_STATE_NAME])
        exp_services._save_exploration('fake@user.com', exp, '', [])

        # Hit the default rule of state 1 once, and the default rule of state 2
        # twice.
        event_services.StateHitEventHandler.record(
            'eid', FIRST_STATE_NAME, True)
        event_services.AnswerSubmissionEventHandler.record(
            'eid', 1, FIRST_STATE_NAME, self.SUBMIT_HANDLER,
            self.DEFAULT_RULESPEC, '1')

        for i in range(2):
            event_services.StateHitEventHandler.record(
                'eid', SECOND_STATE_NAME, True)
            event_services.AnswerSubmissionEventHandler.record(
                'eid', 1, SECOND_STATE_NAME, self.SUBMIT_HANDLER,
                self.DEFAULT_RULESPEC, '1')

        states = stats_services.get_state_improvements('eid')
        self.assertEquals(states, [{
            'rank': 2,
            'type': 'default',
            'state_name': SECOND_STATE_NAME
        }, {
            'rank': 1,
            'type': 'default',
            'state_name': FIRST_STATE_NAME
        }])

        # Hit the default rule of state 1 two more times.
        for i in range(2):
            event_services.StateHitEventHandler.record(
                'eid', FIRST_STATE_NAME, True)
            event_services.AnswerSubmissionEventHandler.record(
                'eid', 1, FIRST_STATE_NAME, self.SUBMIT_HANDLER,
                self.DEFAULT_RULESPEC, '1')

        states = stats_services.get_state_improvements('eid')
        self.assertEquals(states, [{
            'rank': 3,
            'type': 'default',
            'state_name': FIRST_STATE_NAME
        }, {
            'rank': 2,
            'type': 'default',
            'state_name': SECOND_STATE_NAME
        }])


class UnresolvedAnswersTests(test_utils.GenericTestBase):
    """Test the unresolved answers methods."""

    DEFAULT_RULESPEC_STR = exp_domain.DEFAULT_RULESPEC_STR
    DEFAULT_RULESPEC = exp_domain.RuleSpec.get_default_rule_spec(
        'sid', 'NormalizedString')
    SUBMIT_HANDLER = stats_services.SUBMIT_HANDLER_NAME

    def test_get_top_unresolved_answers(self):
        self.assertEquals(
            stats_services.get_top_unresolved_answers_for_default_rule(
                'eid', 'sid'), {})

        event_services.AnswerSubmissionEventHandler.record(
            'eid', 1, 'sid', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC, 'a1')
        self.assertEquals(
            stats_services.get_top_unresolved_answers_for_default_rule(
                'eid', 'sid'), {'a1': 1})

        event_services.AnswerSubmissionEventHandler.record(
            'eid', 1, 'sid', self.SUBMIT_HANDLER, self.DEFAULT_RULESPEC, 'a1')
        self.assertEquals(
            stats_services.get_top_unresolved_answers_for_default_rule(
                'eid', 'sid'), {'a1': 2})

        event_services.DefaultRuleAnswerResolutionEventHandler.record(
            'eid', 'sid', self.SUBMIT_HANDLER, ['a1'])
        self.assertEquals(
            stats_services.get_top_unresolved_answers_for_default_rule(
                'eid', 'sid'), {})


class EventLogEntryTests(test_utils.GenericTestBase):
    """Test for the event log creation."""

    def test_create_events(self):
        """Basic test that makes sure there are no exceptions thrown."""
        event_services.StartExplorationEventHandler.record(
            'eid', 2, 'state', 'session', {}, feconf.PLAY_TYPE_NORMAL)
        event_services.MaybeLeaveExplorationEventHandler.record(
            'eid', 2, 'state', 'session', 27.2, {}, feconf.PLAY_TYPE_NORMAL)
