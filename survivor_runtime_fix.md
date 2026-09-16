# Survivor runtime regression

The Streamlit deployment displayed the new Survivor controls but raised `AttributeError` when saving because the running process could retain a `PoolState` instance whose loaded class did not expose the newly-added instance method. The dashboard now performs the small state mutation through compatibility logic using the stable public state fields, while `state.py` keeps the canonical methods for fresh processes and other callers.
