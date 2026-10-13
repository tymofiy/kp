// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2026 Timothy Kompanchenko
#set page(
  paper: "a4",
  margin: (top: 22mm, bottom: 20mm, left: 20mm, right: 20mm),
  header: context if counter(page).get().first() > 1 {
    text(size: 8pt, fill: rgb("617184"))[KP:1 · RELEASE_VERSION · Released Editor's Draft]
  },
  footer: context align(right, text(size: 8pt, fill: rgb("617184"), counter(page).display("1"))),
)
#set text(font: ("Inter", "Arial Unicode MS"), size: 10pt, fill: rgb("142a40"), lang: "en")
#set par(justify: false, leading: 0.6em, spacing: 0.8em)
#set heading(numbering: none)
#show heading.where(level: 1): set text(size: 21pt, weight: "semibold")
#show heading.where(level: 2): set text(size: 14pt, weight: "semibold")
#show heading.where(level: 3): set text(size: 11pt, weight: "semibold")
#show link: set text(fill: rgb("35677d"))
#show raw: set text(font: ("IBM Plex Mono", "DejaVu Sans Mono", "Arial Unicode MS"), size: 8pt)
#show raw.where(block: true): it => block(width: 100%, inset: 8pt, fill: rgb("f2f5f7"), radius: 3pt, breakable: true, it)
#set table(inset: 4pt, stroke: 0.4pt + rgb("d7dfe5"))
#show table: set text(size: 8pt)
#show figure.where(kind: table): set block(breakable: true)
#let horizontalRule = line(length: 100%, stroke: 0.5pt + rgb("d7dfe5"))
#let divider() = horizontalRule
#let tightlist = it => it
