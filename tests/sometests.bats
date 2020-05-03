load harness

@test "extra-1" {
  check 'x := 3 ; y := 5; if ( x < y ) then x := x + 1 else x := x - 1' '⇒ skip; y := 5; if (x<y) then { x := (x+1) } else { x := (x-1) }, {x → 3}
⇒ y := 5; if (x<y) then { x := (x+1) } else { x := (x-1) }, {x → 3}
⇒ skip; if (x<y) then { x := (x+1) } else { x := (x-1) }, {x → 3, y → 5}
⇒ if (x<y) then { x := (x+1) } else { x := (x-1) }, {x → 3, y → 5}
⇒ x := (x+1), {x → 3, y → 5}
⇒ skip, {x → 4, y → 5}'
}

@test "extra-2" {
  check 'if true < 0 then x := 7 else y := 9' '⇒ y := 9, {}
⇒ skip, {y → 9}'
}

@test "extra-3" {
  check 'z := ( x + 1 ) * -4; y := z * 8' '⇒ skip; y := (z*8), {z → -4}
⇒ y := (z*8), {z → -4}
⇒ skip, {y → -32, z → -4}'
}

@test "extra-4" {
  check 'x := y - -2; y := x + 10' '⇒ skip; y := (x+10), {x → 2}
⇒ y := (x+10), {x → 2}
⇒ skip, {x → 2, y → 12}'
}

@test "extra-5" {
  check 'while x < 8 do x := x + 2' '⇒ x := (x+2); while (x<8) do { x := (x+2) }, {}
⇒ skip; while (x<8) do { x := (x+2) }, {x → 2}
⇒ while (x<8) do { x := (x+2) }, {x → 2}
⇒ x := (x+2); while (x<8) do { x := (x+2) }, {x → 2}
⇒ skip; while (x<8) do { x := (x+2) }, {x → 4}
⇒ while (x<8) do { x := (x+2) }, {x → 4}
⇒ x := (x+2); while (x<8) do { x := (x+2) }, {x → 4}
⇒ skip; while (x<8) do { x := (x+2) }, {x → 6}
⇒ while (x<8) do { x := (x+2) }, {x → 6}
⇒ x := (x+2); while (x<8) do { x := (x+2) }, {x → 6}
⇒ skip; while (x<8) do { x := (x+2) }, {x → 8}
⇒ while (x<8) do { x := (x+2) }, {x → 8}
⇒ skip, {x → 8}'
}
