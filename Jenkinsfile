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
                bat 'taskkill /F /IM python.exe /T 2>nul || echo No existing instance'
                bat 'powershell -Command "Start-Process python -ArgumentList \'-m streamlit run app.py --server.port 8501 --server.headless true\' -WindowStyle Hidden"'
                bat 'timeout /t 6 /nobreak > nul'
                echo '=== Deploy done ==='
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