# islandora7-rest

islandora7-rest is a Python 3+ library for [Discovery Garden's REST interface
for Islandora 7](https://github.com/discoverygarden/islandora_rest)

## Usage 

[Usage.md](https://kulibraries.github.io/islandora7-rest/Usage) in the GitHub project.  
A number of demos are also included in the repo.

## Why?

Islandora is a PHP project? Sure. However, our metadata and curation staff are more fluent in Python and
it is the lingua franca of API manipulation. We are using this library in conjuction with other
Python libraries to move content to and from other REST APIs.

[mjordan/irc](https://github.com/mjordan/irc) covers the same territory in PHP/Guzzle. 

Why not access Fedora more directly? (see Emory's [eulfedora](https://github.com/emory-libraries/eulfedora))? 
1. authentication - most Islandora sites don't have many Fedora users, 
relying on the Drupal DB methods. We're one step further, behind SSO. 
2. hiding Fedora - we don't want to expose our vintage Fedora 3 to anyone.
3. Leverage other Islandora hooks - Ingesting an OBJ, assuming the CModel is correct, 
will cut derivatives correctly. 

### Maintenance

Developed by the University of Kansas IT and Libraries. 

### License

[BSD 3-Clause License](https://opensource.org/licenses/bsd-3-clause).
