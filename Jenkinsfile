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
    stage('mkdocs'){
      agent {
        docker {
          image 'python:3.7'
          args  '-u root'
        }
      }
      steps{
        withCredentials([
          file(credentialsId: 'jenkins-harvestreporting-buildkey', variable: 'GIT_SSH_KEY')
        ]) {
          withEnv([
            // "HOME=${env.WORKSPACE}"
          ]) {
            // Setup Git
            sh 'mkdir ~/.ssh'
            sh "git config core.sshCommand 'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'"
            sh 'git config user.name "JenkinsCI"'
            sh 'git config user.email "DevOpsNow@taos.com"'
            sh 'cp $GIT_SSH_KEY ~/.ssh/id_rsa'
            sh 'git checkout $GIT_BRANCH --force'

            // Generate Docs
            sh 'pip install -r devrequirements.txt'
            sh 'python -m sphinx .docs docs'

            // Commit them to repository
            sh 'git add docs'
            sh 'git commit -m "generating docs with sphinx"'
            sh 'git push'
            //  Try to cleanup to not trigger Jenkins build error
            sh 'rm docs .git -rf'
          }
        }
      }
    }
    stage('deploy'){
      agent { docker { image 'nsnow/opsbot-pipeline-env' }}
      when{
        branch 'master'
      }
      steps{
        withCredentials([
          file(credentialsId: 'devops-gcp-serviceaccount', variable: 'GCP_KEY'),
          string(credentialsId: 'harvest-bearer-token', variable: 'BEARER_TOKEN'),
          string(credentialsId: 'devops-harvest-accountid', variable: 'HARVEST_ID'),
          string(credentialsId: 'devops-now-gcp-project', variable: 'PROJECT'),
          string(credentialsId: 'devops-now-gcp-configbucket', variable: 'BUCKET'),
          string(credentialsId: 'devops-now-gcp-harvestconfigpath', variable: 'CONFIG_PATH'),
          string(credentialsId: 'devops-now-slack-bot-token', variable: 'BOT_TOKEN')
        ]) {
          withEnv(["HOME=${env.WORKSPACE}"]) {
            sh 'gcloud auth activate-service-account --key-file=${GCP_KEY}'
            sh 'gcloud config set project ${PROJECT}'
            sh '''
              gcloud functions deploy harvest_reports --runtime python37 --trigger-topic dailyReport \
                --set-env-vars=BEARER_TOKEN=${BEARER_TOKEN},HARVEST_ACCOUNT_ID=${HARVEST_ID},BUCKET=${BUCKET},CONFIG_PATH=${CONFIG_PATH},SLACK_API_TOKEN=${BOT_TOKEN}
            '''
          }
        }
      }
    }
  }
}
