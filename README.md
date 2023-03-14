Simple TextBurger inspired text adversarial attack.

Usage example:

```
python main.py attack  "Feeling my way through the darkness Guided by a beating heart I can't tell where the journey will end But I know where to start"
; success!
; base label: fear
; new  label: joy
; new text: Feeling my way through the darkness Guided yb a beating heart I can't tell where the journey will end But I know where to start


python main.py attack --line "Feeling my way through the darkness Guided by a beating heart I can't tell where the journey will end But I know where to start"

; base label: joy
; score: 0.9978162050247192
; importance:
; 0.67299053      trusting
; 0.00015914      heart
; 0.00014418      from
; 0.00014311      the
; 0.00012350      how
; 0.00011891      matter
; 0.00011426      no
; 0.00011104      So
; 0.00009376      It
; 0.00007975      we
; 0.00005484      be
; 0.00004369      far
; 0.00004238      more
; 0.00001615      much
; -0.00001699     matters
; -0.00006282     nothing
; -0.00007325     And
; -0.00007838     Forever
; -0.00008833     else
; -0.00009996     are
; -0.00010765     couldn't
; -0.00014544     who
; -0.00019389     close,
; label: anger / score: 0.9781073927879333
; success!
; base label: joy
; new  label: anger
; new text: So close, no matter how far It couldn't be much more from the heart Forever tusting who we are And nothing else matters
```

paper: https://arxiv.org/pdf/1812.05271.pdf
