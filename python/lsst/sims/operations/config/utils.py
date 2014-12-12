# File for holding little utilites

def makeIntDict(ilist):
    """
    This function makes an integer indexed dictionary from a list.

    @param ilist: The list to make the dictionary from.
    @return: An integer indexed dictionary.
    """
    return dict([(i, ilist[i]) for i in range(len(ilist))])
