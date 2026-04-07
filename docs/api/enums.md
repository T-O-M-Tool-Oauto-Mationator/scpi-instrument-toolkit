# Enumerations

All domain-specific string constants are defined as typed enumerations in
`lab_instruments.enums`.  Every member uses the `str, Enum` mixin so enum
values compare equal to their raw strings and can be passed directly to SCPI
write calls without extra conversion.

Import them from the top-level package:

```python
from lab_instruments import WaveformType, DMMMode, CouplingMode, TriggerEdge, SMUSourceMode
```

---

::: lab_instruments.enums.WaveformType

---

::: lab_instruments.enums.DMMMode

---

::: lab_instruments.enums.CouplingMode

---

::: lab_instruments.enums.TriggerEdge

---

::: lab_instruments.enums.TriggerMode

---

::: lab_instruments.enums.SMUSourceMode
