# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
Vagrant.require_version ">= 1.6"

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.box_url = "https://atlas.hashicorp.com/ubuntu/boxes/trusty64/versions/14.04/providers/virtualbox.box"
  config.vm.provision :shell, :path => "build/bootstrap.sh"
  # config.vm.provision :shell, :path => "start.sh", run: "always"
  # config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 8080, host: 8888

  # fix for Windows symlinks
  # Step 1 - run in Windows cmd "fsutil behavior set SymlinkEvaluation L2L:1 R2R:1 L2R:1 R2L:1". Cmd must be opened as administrator
  # Step 2 - add customization to virtualbox into Vagrantfile (lines 17-19)
  # Step 3 - run vagrant up again in a new shell
  config.vm.provider "virtualbox" do |v|
     v.customize ["setextradata", :id, "VBoxInternal2/SharedFoldersEnableSymlinksCreate/vagrant", "1"]
  end
end
