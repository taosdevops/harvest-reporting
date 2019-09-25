pipeline {
  agent { docker { image 'python:3.7' } }

  stages {
    stage('test') {
      steps {
        withEnv(["HOME=${env.WORKSPACE}"]) {
          sh 'pip install --user -r devrequirements.txt'
          sh 'python -m unittest discover'
        }
      }
    }
    stage('deploy'){
      steps{
        withCredentials([
          string(credentialsId: 'harvest-bearer-token', variable: 'BEARER_TOKEN')
        ]) {
          sh 'gcloud functions deploy harvest_reports --runtime python37 --trigger-http'
      }
    }
  }
}
