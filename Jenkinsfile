pipeline {
  agent none 
  stages {
    stage('test') {
      agent { docker { image 'python:3.7' } }
      steps {
        withEnv(["HOME=${env.WORKSPACE}"]) {
          sh 'pip install --user -r devrequirements.txt'
          sh 'python -m unittest discover'
        }
      }
    }
    stage('deploy'){
      agent { docker { image 'nsnow/opsbot-pipeline-env' }} 
      steps{
        withCredentials([
          string(credentialsId: 'harvest-bearer-token', variable: 'BEARER_TOKEN'),
          string(credentialsId: 'devops-harvest-accountid', variable: 'HARVEST_ID'),
          string(credentialsId: 'devops-now-gcp-project', variable: 'PROJECT'),
          file(credentialsId: 'devops-gcp-serviceaccount', variable: 'GCP_KEY')
        ]) {
          sh 'gcloud auth activate-service-account --key-file=${GCP_KEY}'
          sh 'gcloud config set project ${PROJECT}'
          sh 'gcloud functions deploy harvest_reports --runtime python37 --trigger-http --set-env-vars=[BEARER_TOKEN=${BEARER_TOKEN},HARVEST_ACCOUNT_ID=${HARVEST_ID}]'
        }
      }
    }
  }
}
