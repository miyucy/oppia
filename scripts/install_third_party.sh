#!/bin/sh

# Copyright 2013 Google Inc. All Rights Reserved.
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

THIRD_PARTY_DIR=third_party
MACHINE_TYPE=`uname -m`

echo Checking if node.js is installed in third_party
if [ ! -d "$THIRD_PARTY_DIR/node-0.10.1" ]; then
  echo Installing Node.js
  if [ ${MACHINE_TYPE} == 'x86_64' ]; then
    wget http://nodejs.org/dist/v0.10.1/node-v0.10.1-linux-x64.tar.gz -O node-download.tgz
    tar xzf node-download.tgz --directory $THIRD_PARTY_DIR
    mv $THIRD_PARTY_DIR/node-v0.10.1-linux-x64 $THIRD_PARTY_DIR/node-0.10.1
    rm node-download.tgz
  else
    wget http://nodejs.org/dist/v0.10.1/node-v0.10.1-linux-x86.tar.gz -O node-download.tgz
    tar xzf node-download.tgz --directory $THIRD_PARTY_DIR
    mv $THIRD_PARTY_DIR/node-v0.10.1-linux-x86 $THIRD_PARTY_DIR/node-0.10.1
    rm node-download.tgz
  fi
fi


# Static resources.
echo Checking whether angular-ui is installed in third_party
if [ ! -d "$THIRD_PARTY_DIR/static/angular-ui-0.4.0" ]; then
  echo Installing Angular UI
  mkdir -p $THIRD_PARTY_DIR/static/
  wget https://github.com/angular-ui/angular-ui/archive/v0.4.0.zip -O angular-ui-download.zip
  unzip angular-ui-download.zip -d $THIRD_PARTY_DIR/static/
  rm angular-ui-download.zip
fi

echo Checking whether select2 is installed in third_party
if [ ! -d "$THIRD_PARTY_DIR/static/select2-3.4.1" ]; then
  echo Installing select2
  mkdir -p $THIRD_PARTY_DIR/static/
  wget https://github.com/ivaynberg/select2/archive/3.4.1.zip -O select2-download.zip
  unzip select2-download.zip -d $THIRD_PARTY_DIR/static/
  rm select2-download.zip
fi

echo Checking whether jquery is installed in third_party
if [ ! -d "$THIRD_PARTY_DIR/static/jquery-2.0.3" ]; then
  echo Installing JQuery
  mkdir -p $THIRD_PARTY_DIR/static/jquery-2.0.3/
  wget https://ajax.googleapis.com/ajax/libs/jquery/2.0.3/jquery.min.js -O $THIRD_PARTY_DIR/static/jquery-2.0.3/jquery.min.js
fi

echo Checking whether jqueryui is installed in third_party
if [ ! -d "$THIRD_PARTY_DIR/static/jqueryui-1.10.3" ]; then
  echo Installing JQueryUI
  mkdir -p $THIRD_PARTY_DIR/static/jqueryui-1.10.3/
  wget https://ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js -O $THIRD_PARTY_DIR/static/jqueryui-1.10.3/jquery-ui.min.js
fi

echo Checking whether angularjs is installed in third_party
if [ ! -d "$THIRD_PARTY_DIR/static/angularjs-1.0.7" ]; then
  echo Installing AngularJS and angular-sanitize
  mkdir -p $THIRD_PARTY_DIR/static/angularjs-1.0.7/
  wget https://ajax.googleapis.com/ajax/libs/angularjs/1.0.7/angular.js -O $THIRD_PARTY_DIR/static/angularjs-1.0.7/angular.js
  wget https://ajax.googleapis.com/ajax/libs/angularjs/1.0.7/angular.min.js -O $THIRD_PARTY_DIR/static/angularjs-1.0.7/angular.min.js
  wget https://ajax.googleapis.com/ajax/libs/angularjs/1.0.7/angular-resource.min.js -O $THIRD_PARTY_DIR/static/angularjs-1.0.7/angular-resource.min.js
  wget https://ajax.googleapis.com/ajax/libs/angularjs/1.0.7/angular-sanitize.min.js -O $THIRD_PARTY_DIR/static/angularjs-1.0.7/angular-sanitize.min.js

  # Files for tests.
  wget http://code.angularjs.org/1.0.7/angular-mocks.js -O $THIRD_PARTY_DIR/static/angularjs-1.0.7/angular-mocks.js
  wget http://code.angularjs.org/1.0.7/angular-scenario.js -O $THIRD_PARTY_DIR/static/angularjs-1.0.7/angular-scenario.js
fi

echo Checking whether d3.js is installed in third_party
if [ ! -d "$THIRD_PARTY_DIR/static/d3js-3.2.8" ]; then
  echo Installing d3.js
  mkdir -p $THIRD_PARTY_DIR/static/d3js-3.2.8/
  wget https://raw.github.com/mbostock/d3/v3.2.8/d3.min.js -O $THIRD_PARTY_DIR/static/d3js-3.2.8/d3.min.js
fi

echo Checking whether YUI2 is installed in third_party
if [ ! -d "$THIRD_PARTY_DIR/static/yui2-2.9.0" ]; then
  echo Downloading YUI2 JavaScript and CSS files
  mkdir -p $THIRD_PARTY_DIR/static/yui2-2.9.0
  wget "http://yui.yahooapis.com/combo?2.9.0/build/yahoo-dom-event/yahoo-dom-event.js&2.9.0/build/container/container_core-min.js&2.9.0/build/menu/menu-min.js&2.9.0/build/element/element-min.js&2.9.0/build/button/button-min.js&2.9.0/build/editor/editor-min.js" -O $THIRD_PARTY_DIR/static/yui2-2.9.0/yui2-2.9.0.js
  wget "http://yui.yahooapis.com/combo?2.9.0/build/assets/skins/sam/skin.css" -O $THIRD_PARTY_DIR/static/yui2-2.9.0/yui2-2.9.0.css
fi

# For this to work, you must first run
#
#     sudo apt-get install cakephp-scripts
#
echo Checking whether jsrepl is installed in third_party
if [ "$INSTALL_JSREPL" -a ! -d "$THIRD_PARTY_DIR/static/jsrepl" ]; then
  echo Checking whether coffeescript has been installed via node.js
  if [ ! -d "$THIRD_PARTY_DIR/node-0.10.1/lib/node_modules/coffee-script" ]; then
    echo Installing CoffeeScript
    npm install -g coffee-script@1.2.0
  fi
  echo Checking whether uglify has been installed via node.js
  if [ ! -d "$THIRD_PARTY_DIR/node-0.10.1/lib/node_modules/uglify-js" ]; then
    echo Installing uglify
    npm install -g uglify-js
  fi

  echo Downloading jsrepl
  cd $THIRD_PARTY_DIR
  git clone git://github.com/replit/jsrepl.git
  cd jsrepl
  git submodule update --init --recursive

  echo Compiling jsrepl
  # Reducing jvm memory requirement from 4G to 1G.
  sed -i s/Xmx4g/Xmx1g/ Cakefile
  # This version of node uses fs.exitsSync.
  sed -i s/path\.existsSync/fs\.existsSync/ Cakefile
  # CoffeeScript is having trouble with octal representation.
  sed -i s/0o755/493/ Cakefile
  NODE_PATH=../node-0.10.1/lib/node_modules cake bake

  cd ../../
  mv $THIRD_PARTY_DIR/jsrepl/build $THIRD_PARTY_DIR/static/jsrepl
fi