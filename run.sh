#!/bin/bash

PID_DIR="./pids"
BACKEND_PID_FILE="$PID_DIR/backend.pid"
FRONTEND_PID_FILE="$PID_DIR/frontend.pid"

# 创建 pid 目录
mkdir -p $PID_DIR

function start_backend() {
    echo "Starting backend service..."
    cd backend && python main.py & echo $! > $BACKEND_PID_FILE
    echo "Backend service started with PID $(cat $BACKEND_PID_FILE)"
}

function start_frontend() {
    echo "Starting frontend service..."
    cd frontend && npm run dev & echo $! > $FRONTEND_PID_FILE
    echo "Frontend service started with PID $(cat $FRONTEND_PID_FILE)"
}

function stop_backend() {
    if [ -f $BACKEND_PID_FILE ]; then
        echo "Stopping backend service..."
        kill -15 $(cat $BACKEND_PID_FILE) 2>/dev/null || echo "Backend service not running"
        rm $BACKEND_PID_FILE
    else
        echo "Backend service not running"
    fi
}

function stop_frontend() {
    if [ -f $FRONTEND_PID_FILE ]; then
        echo "Stopping frontend service..."
        kill -15 $(cat $FRONTEND_PID_FILE) 2>/dev/null || echo "Frontend service not running"
        rm $FRONTEND_PID_FILE
    else
        echo "Frontend service not running"
    fi
}

case "$1" in
    "boss"|"backend")
        case "$2" in
            "stop")
                stop_backend
                ;;
            *)
                start_backend
                ;;
        esac
        ;;
    "web"|"frontend")
        case "$2" in
            "stop")
                stop_frontend
                ;;
            *)
                start_frontend
                ;;
        esac
        ;;
    "all")
        case "$2" in
            "stop")
                stop_frontend
                stop_backend
                ;;
            *)
                # 启动所有服务
                start_frontend
                start_backend
                ;;
        esac
        ;;
    *)
        echo "Usage: $0 {boss|web|all} [stop]"
        echo "  boss      - Manage backend service"
        echo "  web       - Manage frontend service"
        echo "  all       - Manage both services"
        echo ""
        echo "Examples:"
        echo "  $0 boss      - Start backend service"
        echo "  $0 boss stop - Stop backend service"
        echo "  $0 web       - Start frontend service"
        echo "  $0 web stop  - Stop frontend service"
        echo "  $0 all       - Start all services"
        echo "  $0 all stop  - Stop all services"
        exit 1
        ;;
esac 