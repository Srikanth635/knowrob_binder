#!/bin/bash

# Initialize conda
source /opt/conda/etc/profile.d/conda.sh
conda activate agentic_ai311

# source ros ws
source ${ROS_WS}/devel/setup.bash

# Start MongoDB and save data on working directory
MONGODB_URL=mongodb://127.0.0.1:27017
mkdir -p ${PWD}/mongodb/data
# Store MongoDB data under directory ${HOME}/data/db
# mongod --fork --logpath ${HOME}/mongod.log
mongod --fork --logpath ${PWD}/mongodb/mongod.log --dbpath ${PWD}/mongodb/data

# Start Flask application in background
cd ${HOME}/LLM_Reasoner/src/langchain
python flask_graph.py &
FLASK_PID=$!

# Give Flask some time to start
sleep 5

# Return to original directory
cd ${HOME}/knowrob_binder

# jupyterlab UI workspace
jupyter lab workspaces import ${PWD}/binder/jupyterlab.jupyterlab-workspace

# Function to cleanup background processes on exit
cleanup() {
    echo "Cleaning up background processes..."
    kill $FLASK_PID 2>/dev/null
    mongod --shutdown 2>/dev/null
    exit 0
}

# Trap signals to cleanup
trap cleanup SIGTERM SIGINT

exec "$@"