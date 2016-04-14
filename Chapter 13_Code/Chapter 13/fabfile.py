from fabric.api import env, local, run, sudo, cd, settings

env.hosts = ['user@host']


def test():
    local('python -m unittest discover')


def upgrade_libs():
    sudo("apt-get update")
    sudo("apt-get upgrade")


def setup():
    upgrade_libs()

    sudo("apt-get install -y build-essential")
    # sudo("apt-get install -y nginx")
    # sudo("apt-get install -y apache2")
    # sudo("apt-get install -y libapache2-mod-proxy-uwsgi")
    sudo("apt-get install -y git")
    sudo("apt-get install -y python")
    sudo("apt-get install -y python-pip")
    sudo("apt-get install -y python-all-dev")

    with settings(warn_only=True):
        result = run('id deploy')
    if result.failed:
        run("useradd -d /home/deploy/ deploy")
        run("gpasswd -a deploy sudo")

    sudo("chown -R deploy /usr/local/")
    sudo("chown -R deploy /usr/lib/python2.7/")

    run("git config --global credential.helper store")

    with cd("/home/deploy/"):
        run("git clone http://yourgitrepo.com")

    with cd('/home/deploy/webapp'):
        run("pip install -r requirements.txt")
        run("python manage.py createdb")


def deploy():
    test()

    with cd('/home/deploy/webapp'):
        run("git pull")
        run("pip install -r requirements.txt")

        sudo("cp supervisord.conf /etc/supervisor/conf.d/webapp.conf")

        sudo("cp nginx.conf /etc/nginx/sites-available/your_domain")
        sudo("ln -sf /etc/nginx/sites-available/your_domain "
             "/etc/nginx/sites-enabled/your_domain")

        sudo("cp apache.conf /etc/apache2/sites-available/your_domain")
        sudo("ln -sf /etc/apache2/sites-available/your_domain "
             "/etc/apache2/sites-enabled/your_domain")

    sudo("service nginx restart")
    sudo("service apache2 restart")
