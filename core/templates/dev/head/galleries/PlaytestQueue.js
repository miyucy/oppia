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
 * @fileoverview Data and controllers for the Oppia playtesters' queue page.
 *
 * @author sll@google.com (Sean Lip)
 */

oppia.directive('playtestQueueSection', [function() {
  return {
    restrict: 'E',
    scope: {
      explorations: '='
    },
    templateUrl: 'playtestQueue/main',
    controller: ['$scope', 'oppiaDatetimeFormatter', function($scope, oppiaDatetimeFormatter) {
      $scope.getLocaleStringForDate = function(millisSinceEpoch) {
        return oppiaDatetimeFormatter.getLocaleString(millisSinceEpoch);
      };
    }]
  };
}]);

oppia.controller('PlaytestQueue', ['$scope', '$http', '$rootScope', function(
    $scope, $http, $rootScope) {
  $scope.playtestQueueDataUrl = '/playtesthandler/data';

  $rootScope.loadingMessage = 'Loading';

  // Retrieves data from the server.
  $http.get($scope.playtestQueueDataUrl).success(function(data) {
    $scope.publicExplorations = data.public_explorations_list;
    $scope.privateExplorations = data.private_explorations_list;
    $rootScope.loadingMessage = '';
  });
}]);
