#!/bin/bash

mode=$1

function run()
{
  pushd ./../pdmSim/
  ./sim.sh run
  popd
  echo 'Starting custom image and container build for ARIMA...'
  docker-compose up -d
}

function rm()
{
  #disconnect arima container from the simulation network
  docker network disconnect pdmsim_simnet arima
  pushd ./../pdmSim/
  ./sim.sh rm
  popd
  echo 'Removing custom image and container build for ARIMA...'
  docker-compose down --rmi all -v
}

if [ $mode == 'run' ]
then
  run
  exit
fi

if [ $mode == 'rm' ]
then
  rm
  exit
fi

if [ $mode == 'reload' ]
then
  rm
  run
  exit
fi

echo 'sim.sh: Invalid argument!'