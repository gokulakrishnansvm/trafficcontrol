#!/bin/bash
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

set -o errexit

gray_bg="$(printf '%s%s' $'\x1B' '[100m')";
red_bg="$(printf '%s%s' $'\x1B' '[41m')";
yellow_bg="$(printf '%s%s' $'\x1B' '[43m')";
black_fg="$(printf '%s%s' $'\x1B' '[30m')";
color_and_prefix() {
	color="$1";
	shift;
	prefix="$1";
	normal_bg="$(printf '%s%s' $'\x1B' '[49m')";
	normal_fg="$(printf '%s%s' $'\x1B' '[39m')";
	sed "s/^/${color}${black_fg}${prefix}: /" | sed "s/$/${normal_bg}${normal_fg}/";
}

export GOPATH="${HOME}/go"
org_dir="$GOPATH/src/github.com/apache"
repo_dir="${org_dir}/trafficcontrol"
if [[ ! -e "$repo_dir" ]]; then
	mkdir -p "$org_dir"
	cd
	mv "${GITHUB_WORKSPACE}" "${repo_dir}/"
	ln -s "$repo_dir" "${GITHUB_WORKSPACE}"
fi

cd "${repo_dir}/traffic_ops/traffic_ops_golang"


resources="$(dirname "$0")"
envsubst <"${resources}/cdn.json" >cdn.conf
cp "${resources}/database.json" database.conf

./traffic_ops_golang --cfg ./cdn.conf --dbcfg ./database.conf &

cd "../testing/api_contract/v$INPUT_VERSION"

pytest