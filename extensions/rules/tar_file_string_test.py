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
# Unless required by applicable law or agreed to in writing, softwar
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for classification of TarFileStrings."""

__author__ = 'Tarashish Mishra'

import base64
import os
import unittest

from core.domain import fs_domain
from extensions.rules import tar_file_string
import utils


TEST_DATA_DIR = os.path.join('extensions', 'rules', 'testdata')


class TarFileStringRuleUnitTests(unittest.TestCase):
    """Tests for rules operating on UnicodeString objects."""

    def test_wrapper_name_rule(self):
        rule = tar_file_string.ChecksWrapperDirName('myproject-0.1')

        file_name = 'wrong-wrapper-name.tar.gz'
        encoded_content = base64.b64encode(utils.get_file_contents(
            os.path.join(TEST_DATA_DIR, file_name), raw_bytes=True, mode='rb'))
        self.assertTrue(rule.eval(encoded_content))

        file_name = 'good.tar.gz'
        encoded_content = base64.b64encode(utils.get_file_contents(
            os.path.join(TEST_DATA_DIR, file_name), raw_bytes=True, mode='rb'))
        self.assertFalse(rule.eval(encoded_content))

    def test_wrapper_presence_rule(self):
        rule = tar_file_string.ChecksWrapperDirPresence()

        file_name = 'no-wrapper-dir.tar.gz'
        encoded_content = base64.b64encode(utils.get_file_contents(
            os.path.join(TEST_DATA_DIR, file_name), raw_bytes=True, mode='rb'))
        self.assertTrue(rule.eval(encoded_content))

        file_name = 'good.tar.gz'
        encoded_content = base64.b64encode(utils.get_file_contents(
            os.path.join(TEST_DATA_DIR, file_name), raw_bytes=True, mode='rb'))
        self.assertFalse(rule.eval(encoded_content))

    def test_unexpected_file_rule(self):
        rule = tar_file_string.HasUnexpectedFile(
            ["myproject-0.1", "myproject-0.1/hello.c",
             "myproject-0.1/Makefile"]
        )

        file_name = 'unexpected-file.tar.gz'
        encoded_content = base64.b64encode(utils.get_file_contents(
            os.path.join(TEST_DATA_DIR, file_name), raw_bytes=True, mode='rb'))
        self.assertTrue(rule.eval(encoded_content))

        file_name = 'good.tar.gz'
        encoded_content = base64.b64encode(utils.get_file_contents(
            os.path.join(TEST_DATA_DIR, file_name), raw_bytes=True, mode='rb'))
        self.assertFalse(rule.eval(encoded_content))

    def test_unexpected_content_rule(self):
        fs = fs_domain.AbstractFileSystem(
            fs_domain.DiskBackedFileSystem(TEST_DATA_DIR))

        CANONICAL_DATA_DIR = os.path.join(TEST_DATA_DIR, 'canonical')
        canonical_fs = fs_domain.AbstractFileSystem(
            fs_domain.DiskBackedFileSystem(CANONICAL_DATA_DIR))

        rule = tar_file_string.HasUnexpectedContent(
            ['hello.c', 'Makefile']).set_fs(canonical_fs)

        file_name = 'incorrect-contents.tar.gz'
        encoded_content = base64.b64encode(fs.get(file_name, mode='rb'))
        self.assertTrue(rule.eval(encoded_content))

        file_name = 'good.tar.gz'
        encoded_content = base64.b64encode(fs.get(file_name, mode='rb'))
        self.assertFalse(rule.eval(encoded_content))

    def test_missing_expected_file_rule(self):
        rule = tar_file_string.MissingExpectedFile(
            ["myproject-0.1", "myproject-0.1/hello.c",
             "myproject-0.1/Makefile"]
        )

        file_name = 'missing-expected-file.tar.gz'
        encoded_content = base64.b64encode(utils.get_file_contents(
            os.path.join(TEST_DATA_DIR, file_name), raw_bytes=True, mode='rb'))
        self.assertTrue(rule.eval(encoded_content))

        file_name = 'good.tar.gz'
        encoded_content = base64.b64encode(utils.get_file_contents(
            os.path.join(TEST_DATA_DIR, file_name), raw_bytes=True, mode='rb'))
        self.assertFalse(rule.eval(encoded_content))

    def test_apple_double_file_rule(self):
        rule = tar_file_string.HasAppleDoubleFile()

        file_name = 'apple-double.tar.gz'
        encoded_content = base64.b64encode(utils.get_file_contents(
            os.path.join(TEST_DATA_DIR, file_name), raw_bytes=True, mode='rb'))
        self.assertTrue(rule.eval(encoded_content))

        file_name = 'good.tar.gz'
        encoded_content = base64.b64encode(utils.get_file_contents(
            os.path.join(TEST_DATA_DIR, file_name), raw_bytes=True, mode='rb'))
        self.assertFalse(rule.eval(encoded_content))
