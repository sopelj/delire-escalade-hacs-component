# Délire Escalade Occupancy Sensor

A sensor to display the occupancy of the [Délire Climbing gyms](https://www.delirescalade.com/) in Québec.
A temporary measure in place for Covid. But I check it often enough that this is useful for me. Perhaps you as well.

## Installation

Add to HACS as custom repository:

<https://github.com/sopelj/delire-escalade-hacs-component>

And then add to your configuration.yaml and choose which Gyms you want to add sensors for:

```yaml
sensors:
  - platform: de_occupancy
    gyms:
      - beauport
      - pierrebertrand
      - stefoy
```
