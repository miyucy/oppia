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
 * @fileoverview Initialization and basic configuration for the Oppia module.
 *
 * @author sll@google.com (Sean Lip)
 */

// TODO(sll): Remove the check for window.GLOBALS. This check is currently
// only there so that the Karma tests run, since it looks like Karma doesn't
// 'see' the GLOBALS variable that is defined in base.html. We should fix this
// in order to make the testing and production environments match.
var oppia = angular.module(
  'oppia',
  ['ngSanitize', 'ngResource', 'ui.bootstrap', 'ui.sortable'].concat(
    window.GLOBALS ? (window.GLOBALS.ADDITIONAL_ANGULAR_MODULES || [])
                   : []));

// Set the AngularJS interpolators as <[ and ]>, to not conflict with Jinja2
// templates.
// Set default headers for POST and PUT requests.
// Add an interceptor to convert requests to strings and to log and show
// warnings for error responses.
oppia.config(['$interpolateProvider', '$httpProvider',
    function($interpolateProvider, $httpProvider) {
  $interpolateProvider.startSymbol('<[');
  $interpolateProvider.endSymbol(']>');

  $httpProvider.defaults.headers.post = {
    'Content-Type': 'application/x-www-form-urlencoded'};
  $httpProvider.defaults.headers.put = {
    'Content-Type': 'application/x-www-form-urlencoded'};

  $httpProvider.interceptors.push([
    '$q', '$log', 'warningsData', function($q, $log, warningsData) {
      return {
        request: function(config) {
          // If this request carries data (in the form of a JS object),
          // JSON-stringify it and store it under 'payload'.
          if (config.data) {
            config.data = $.param({
              csrf_token: GLOBALS.csrf_token,
              payload: JSON.stringify(config.data),
              source: document.URL
            }, true);
          }
          return config;
        },
        responseError: function(response) {
          $log.error(response.data);
          warningsData.addWarning(
            response.data.error || 'Error communicating with server.');
          return $q.reject(response);
        }
      };
    }
  ]);
}]);

oppia.config(['$provide', function($provide) {
  $provide.decorator('$log', ['$delegate', function($delegate) {
    var _originalError = $delegate.error;

    if (window.GLOBALS && !window.GLOBALS.DEV_MODE) {
      $delegate.log = function(message) { };
      $delegate.info = function(message) { };
      // TODO(sll): Send errors (and maybe warnings) to the backend.
      $delegate.warn = function(message) { };
      $delegate.error = function(message) {
        if (String(message).indexOf('$digest already in progress') === -1) {
          _originalError(message);
        }
      };
      $delegate.error.logs = [];  // This keeps angular-mocks happy (in tests).
    }

    return $delegate;
  }]);
}]);

// Overwrite the built-in exceptionHandler service to log errors to the backend
// (so that they can be fixed).
oppia.factory('$exceptionHandler', ['$log', function($log) {
  return function(exception, cause) {
    var messageAndSourceAndStackTrace = [
      '',
      'Source: ' + window.location.href,
      exception.message,
      String((new Error()).stack)
    ].join('\n');

    // Catch all errors, to guard against infinite recursive loops.
    try {
      // We use jQuery here instead of Angular's $http, since the latter
      // creates a circular dependency.
      $.ajax({
        type: 'POST',
        url: '/frontend_errors',
        data: $.param({
          csrf_token: GLOBALS.csrf_token,
          payload: JSON.stringify({error: messageAndSourceAndStackTrace}),
          source: document.URL
        }, true),
        contentType: 'application/x-www-form-urlencoded',
        dataType: 'text',
        async: true
      });
    } catch(loggingError) {
      $log.warn('Error logging failed.');
    }

    $log.error.apply($log, arguments);
  };
}]);

// Service for HTML serialization and escaping.
oppia.factory('oppiaHtmlEscaper', ['$log', function($log) {
  var htmlEscaper = {
    objToEscapedJson: function(obj) {
      return this.unescapedStrToEscapedStr(JSON.stringify(obj));
    },
    escapedJsonToObj: function(json) {
      if (!json) {
        $log.error('Empty string was passed to JSON decoder.');
        return '';
      }
      return JSON.parse(this.escapedStrToUnescapedStr(json));
    },
    unescapedStrToEscapedStr: function(str) {
      return String(str)
                  .replace(/&/g, '&amp;')
                  .replace(/"/g, '&quot;')
                  .replace(/'/g, '&#39;')
                  .replace(/</g, '&lt;')
                  .replace(/>/g, '&gt;');
    },
    escapedStrToUnescapedStr: function(value) {
      return String(value)
                  .replace(/&quot;/g, '"')
                  .replace(/&#39;/g, "'")
                  .replace(/&lt;/g, '<')
                  .replace(/&gt;/g, '>')
                  .replace(/&amp;/g, '&');
    }
  };
  return htmlEscaper;
}]);

// Service for converting dates in milliseconds since the Epoch to
// human-readable dates.
oppia.factory('oppiaDatetimeFormatter', [function() {
  return {
    getHumanReadableDatetime: function(millisSinceEpoch) {
      var date = new Date(millisSinceEpoch);
      return date.toUTCString();
    },
    getLocaleString: function(millisSinceEpoch) {
      var date = new Date(millisSinceEpoch);
      return date.toLocaleString();
    },
    // Returns time of the day if milliseconds since the Epoch
    // translates to current date otherwise returns the date.
    getLocaleAbbreviatedDatetimeString: function(millisSinceEpoch) {
      var date = new Date(millisSinceEpoch);
      if (date.toLocaleDateString() == new Date().toLocaleDateString()) {
        // The replace function removes 'seconds' from the time returned.
        return date.toLocaleTimeString().replace(/:\d\d /, ' ');
      }
      return date.toLocaleDateString();
    }
  };
}]);

// Service for validating things and (optionally) displaying warning messages
// if the validation fails.
oppia.factory('validatorsService', [
    '$filter', 'warningsData', function($filter, warningsData) {
  return {
    /**
     * Checks whether an entity name is valid, and displays a warning message
     * if it isn't.
     * @param {string} input The input to be checked.
     * @param {boolean} showWarnings Whether to show warnings in the butterbar.
     * @return {boolean} True if the entity name is valid, false otherwise.
     */
    isValidEntityName: function(input, showWarnings) {
      input = $filter('normalizeWhitespace')(input);
      if (!input) {
        if (showWarnings) {
          warningsData.addWarning('Please enter a non-empty name.');
        }
        return false;
      }

      for (var i = 0; i < GLOBALS.INVALID_NAME_CHARS.length; i++) {
        if (input.indexOf(GLOBALS.INVALID_NAME_CHARS[i]) !== -1) {
          if (showWarnings) {
            warningsData.addWarning(
             'Invalid input. Please use a non-empty description consisting ' +
             'of alphanumeric characters, underscores, spaces and/or hyphens.'
            );
          }
          return false;
        }
      }
      return true;
    },
    isNonempty: function(input, showWarnings) {
      if (!input) {
        if (showWarnings) {
          // TODO(sll): Allow this warning to be more specific in terms of what
          // needs to be entered.
          warningsData.addWarning('Please enter a non-empty value.');
        }
        return false;
      }
      return true;
    }
  }
}]);

// Service for setting focus. This broadcasts a 'focusOn' event which sets
// focus to the element in the page with the corresponding focusOn attribute.
oppia.factory('focusService', ['$rootScope', '$timeout', function($rootScope, $timeout) {
  return {
    setFocus: function(name) {
      $timeout(function() {
        $rootScope.$broadcast('focusOn', name);
      });
    }
  };
}]);

// Add a String.prototype.trim() polyfill for IE8.
if (typeof String.prototype.trim !== 'function') {
  String.prototype.trim = function() {
    return this.replace(/^\s+|\s+$/g, '');
  };
}

// Add an Object.create() polyfill for IE8.
if (typeof Object.create !== 'function') {
  (function() {
    var F = function() {};
    Object.create = function(o) {
      if (arguments.length > 1) {
        throw Error('Second argument for Object.create() is not supported');
      }
      if (o === null) {
        throw Error('Cannot set a null [[Prototype]]');
      }
      if (typeof o !== 'object') {
        throw TypeError('Argument must be an object');
      }
      F.prototype = o;
      return new F();
    };
  })();
}
