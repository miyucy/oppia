// Copyright 2014 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Controllers for the graphical state editor.
 *
 * @author sll@google.com (Sean Lip)
 */

oppia.controller('StateEditor', [
  '$scope', '$filter', 'explorationData', 'warningsData',
  'editorContextService', 'changeListService', 'validatorsService',
  'focusService', function(
    $scope, $filter, explorationData, warningsData,
    editorContextService, changeListService, validatorsService,
    focusService) {

  $scope.$on('refreshStateEditor', function(evt) {
    $scope.initStateEditor();
  });

  $scope.initStateEditor = function() {
    explorationData.getData().then(function(data) {
      $scope.paramSpecs = data.param_specs || {};
    });

    $scope.stateNameEditorIsShown = false;

    $scope.stateName = editorContextService.getActiveStateName();
    var stateData = $scope.$parent.states[$scope.stateName];
    $scope.content = stateData.content || [];
    $scope.stateParamChanges = stateData.param_changes || [];

    // This should only be non-null when the content editor is open.
    $scope.contentMemento = null;

    if ($scope.stateName && stateData) {
      $scope.$broadcast('stateEditorInitialized', stateData);
    }
  };

  $scope.openStateNameEditor = function() {
    $scope.stateNameEditorIsShown = true;
    $scope.tmpStateName = $scope.stateName;
    $scope.stateNameMemento = $scope.stateName;
    focusService.setFocus('stateNameEditorOpened');
  };

  $scope._getNormalizedStateName = function(newStateName) {
    return $filter('normalizeWhitespace')(newStateName);
  };

  $scope.saveStateNameAndRefresh = function(newStateName) {
    var normalizedStateName = $scope._getNormalizedStateName(newStateName);
    var valid = $scope.saveStateName(normalizedStateName);
    if (valid) {
      $scope.$parent.showStateEditor(normalizedStateName);
    }
  };

  $scope.saveStateName = function(newStateName) {
    newStateName = $scope._getNormalizedStateName(newStateName);
    if (!validatorsService.isValidEntityName(newStateName, true)) {
      return false;
    }
    if (newStateName.length > 50) {
      warningsData.addWarning(
        'State names should be at most 50 characters long.');
      return false;
    }
    var activeStateName = editorContextService.getActiveStateName();
    if (newStateName !== activeStateName &&
        $scope.states.hasOwnProperty(newStateName)) {
      warningsData.addWarning(
        'The name \'' + newStateName + '\' is already in use.');
      return false;
    }

    if ($scope.stateNameMemento === newStateName) {
      $scope.stateNameEditorIsShown = false;
      return false;
    } else {
      // Tidy up the rest of the states.
      // TODO(sll): Pull initStateName out into a service.
      if ($scope.$parent.$parent.initStateName == activeStateName) {
        $scope.$parent.$parent.initStateName = newStateName;
      }

      $scope.states[newStateName] = angular.copy(
        $scope.states[activeStateName]);
      delete $scope.states[activeStateName];
      for (var otherStateName in $scope.states) {
        var handlers = $scope.states[otherStateName].widget.handlers;
        for (var i = 0; i < handlers.length; i++) {
          for (var j = 0; j < handlers[i].rule_specs.length; j++) {
            if (handlers[i].rule_specs[j].dest === activeStateName) {
              handlers[i].rule_specs[j].dest = newStateName;
            }
          }
        }
      }

      editorContextService.setActiveStateName(newStateName);
      changeListService.renameState(newStateName, $scope.stateNameMemento);

      $scope.stateNameEditorIsShown = false;
      $scope.refreshGraph();
      $scope.initStateEditor();
      return true;
    }
  };

  $scope.editContent = function() {
    $scope.contentMemento = angular.copy($scope.content);
  };

  $scope.$on('externalSave', function() {
    $scope.saveTextContent();
    if ($scope.stateNameEditorIsShown) {
      $scope.saveStateName($scope.tmpStateName);
    }
  });

  $scope.saveTextContent = function() {
    if ($scope.contentMemento !== null && $scope.contentMemento !== $scope.content) {
      changeListService.editStateProperty(
        editorContextService.getActiveStateName(), 'content',
        angular.copy($scope.content), angular.copy($scope.contentMemento));
    }
    $scope.contentMemento = null;
  };

  $scope.saveStateParamChanges = function(newValue, oldValue) {
    if (!angular.equals(newValue, oldValue)) {
      changeListService.editStateProperty(
        editorContextService.getActiveStateName(), 'param_changes',
        newValue, oldValue);
    }
  };
}]);
