pipeline {
    agent any

    triggers {
        pollSCM('H/5 * * * *')
    }

    environment {
        MONGO_URI  = "mongodb+srv://admin:12345@movierecommender.gu56d6o.mongodb.net/?appName=movierecommender"
        NEO4J_URI  = "bolt://localhost:7687"
        NEO4J_USER = "neo4j"
        NEO4J_PASS = "12345678"
    }

    stages {

        stage('Checkout') {
            steps {
                echo '=== Pulling latest code from GitHub ==='
                checkout scmGit(
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        credentialsId: 'github-creds',
                        url: 'https://github.com/orwin1002/movierecommender.git'
                    ]]
                )
            }
        }

        stage('Build') {
            steps {
                echo '=== Installing Python dependencies ==='
                sh '''
                    python3 -m pip install --upgrade pip --quiet
                    pip3 install -r requirements.txt --quiet
                '''
            }
        }

        stage('Test') {
            steps {
                echo '=== Running pytest on mood logic ==='
                sh 'python3 -m pytest tests/ -v --tb=short'
            }
        }

        stage('Deploy') {
            steps {
                echo '=== Stopping any existing Streamlit instance ==='
                sh 'pkill -f "streamlit run" || true'
                sh 'sleep 3'

                echo '=== Starting MoodReel app ==='
                sh '''
                    nohup python3 -m streamlit run app.py \
                        --server.port 8501 \
                        --server.headless true \
                        > streamlit.log 2>&1 &
                    sleep 6
                    echo "Deploy done"
                '''
            }
        }

        stage('Health Check') {
            steps {
                echo '=== Verifying app is responding ==='
                sh '''
                    curl -f http://localhost:8501/_stcore/health \
                        && echo "✅ App is live at localhost:8501" \
                        || (echo "❌ Health check failed" && exit 1)
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline complete — MoodReel is live!'
        }
        failure {
            echo '❌ Pipeline failed — killing any broken deployment'
            sh 'pkill -f "streamlit run" || true'
        }
    }
}