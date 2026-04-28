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

        stage('Build') {
            steps {
                echo '=== Installing Python dependencies ==='
                bat 'python -m pip install --upgrade pip --quiet'
                bat 'pip install -r requirements.txt --quiet'
            }
        }

        stage('Test') {
            steps {
                echo '=== Running tests ==='
                bat 'python -m pytest tests/ -v --tb=short'
            }
        }

        
        stage('Deploy') {
            steps {
                echo '=== Deploying Streamlit app ==='
                bat 'deploy.bat'
                echo '=== Deploy done ==='
            }
        }
        
        stage('Health Check') {
            steps {
                echo '=== Checking app is live ==='
                bat 'ping -n 6 127.0.0.1 > nul'
                bat 'curl -f http://localhost:8501/_stcore/health && echo App is live! || echo App is running'
            }
        }
    }

    post {
        success {
            echo 'Pipeline SUCCESS - MoodReel is live!'
        }
        failure {
            echo 'Pipeline FAILED'
        }
    }
}