# like, if we're gonna take text from a buffer, but only middle part of lines
# is the "actual", makes sense to have this class handling the duties of
# splitting the lines, sending them to the correct metabuffers etc?

# or maybe doesnt need to be that complicated, not sure.
# but reckon might be better than having like a billion DummyBuffer
# derivatives handling all their shit themselves.

# this is sorta the core confusion anyways, how our "Buffer" object has to
# represent both what's 'possible' and the concrete state in vim.
# Leading to the question, do you let Buffer do everything, or have logic
# elsewhere and return results to Buffer for display, 
