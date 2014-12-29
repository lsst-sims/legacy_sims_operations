
"""
LSSTObject

Inherits from: object

Class Description
LSSTObject is the root class of the (non SimPy) classes. It inherits 
directly from the Python root class object.

Its main role is to provide a way to nicely format the string 
representation of classes and objects.


Method Types
String Representation
- __str__
"""

class LSSTObject (object):
    def __str__ (self):
        """
        Override of the default __str__ method. Provide a nice format
        to each instance string representation.
        
        It is never called explicitly, rather it is invoked by the
        cast to a string.
        """
        strRepr = '%s:\n' % (self.__module__)       # hack
        for attr in self.__dict__.keys ():
            value = getattr (self, attr)
            if (isinstance (value, tuple) or isinstance (value, list)):
                if (len (value)):
                    subStr = ''
                    for element in value:
                        text = str (element).split ('\n')
                        for s in text:
                            subStr += '     %s\n' % (str (s))
                    strRepr += '  %s:\n%s' % (attr, subStr)
                else:
                    strRepr += '  %s: []\n' % (attr)
            else:
                if (str (value).find ('\n') != -1):
                    subStr = type (value)
                else:
                    subStr = value
                strRepr += '  %s: %s\n' % (attr, subStr)
        strRepr = strRepr[:-1]
        return (strRepr)
    