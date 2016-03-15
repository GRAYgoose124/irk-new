## IRK: IRC Bot

### ABOUT
Just your average IRC bot written in python.    
Written by Grayson Miller.       
                            
### LICENSE
Irk is licensed under the GNU Affero General Public License v3.
Refer to the LICENSE file before using Irk.   


## INSTALLING & RUNNING
### Requirements for unit testing
* `nose`   
    
### Testing from source root using unit tests. (no install)
`$ nosetests --nocapture`

### Installing from CLI. (Please use virtualenv)
`$ git clone git@github.com:GRAYgoose124/irk.git irk`  
`$ cd irk`                                           
`$ python setup.py install`                       

### Running after installation.
`$ irk`   
(`CTRL+C` to safely quit or send the `!quit` command)
                                     
### Uninstalling
`$ pip uninstall irk`                                


## PROJECT STATUS
* Version 0.3b

### FEATURES

### PLANNED FEATURES

### FAQ

### BUGS

## TODO (IN PROGRESS)
* TOP TODO
  * Plugin overhaul - make it import packages or files and multiple functions/global imports
    * Allow plugin interaction
    * Plugin packages with global imports
  * Factoids
  * Permissions

* Bug fixes
  * Check all file loading. (filenames, paths, etc)
* Plugins
  * Make Plugins either Single File or Packages
  * Ideas
    * IRC Logging by server/channel
    * Reddit Plugin
  * Permissions (General?)
  * Cross-Plugin Interaction
  * Threading?
  * Document API
    * Data passed to plugin
    * Handler functions
    * Available Hooks (Defined in IrcClient, Instantiated in Bot)
* Proper Debug Logging
* Housecleaning
  * Documentation / API / Comments