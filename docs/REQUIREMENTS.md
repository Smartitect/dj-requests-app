# DJ Requests App — Requirements

## Overview

A lightweight web app that allows audience members to search the Spotify catalogue and submit song requests directly to the DJ's playlist, without needing a Spotify account themselves.

The DJ can refresh their Spotify playlist at any time to see incoming requests, then drag tracks into their performance workflow (e.g. Rekordbox).

---

## Personas

### DJ

Playing and mixing recorded music at a pub, club, or party.

Audience members frequently approach to shout requests over the loud music, which is impractical. The DJ wants a better way for people to submit requests from their mobile phone.

The DJ uses Spotify as a core part of their workflow, connecting Rekordbox to Spotify to stream and mix music via a FLX4 interface.

### Member of the Audience

Attending a party and enjoying the music. They would like the DJ to play a favourite song but may be too shy or unable to ask in person.

They do not have a Spotify account and have no interest in creating one — they may use a different service such as YouTube Music.

They scan a QR code displayed at the venue, which takes them to a simple website where they can search for and submit a request from their phone.

---

## User Stories

### DJ

**Config:** As a DJ, I want to configure the app using a simple config file in the repository, specifying the name of the Spotify playlist used to capture requests. The default playlist name is `"DJ Requests"`.

**Credentials:** As a DJ, I want to store my Spotify API credentials in a local config file that is excluded from source control via `.gitignore`.

**Requests:** As a DJ, as audience members submit requests via the app, I want each requested track to appear in the configured Spotify playlist so I can review and act on them.

### Member of the Audience

**Browsing and requesting:** As a member of the audience, I want to scan a QR code on my phone and be taken to a simple website where I can:

- Search the Spotify catalogue by song title or artist name.
- Browse a list of matching tracks showing song title, artist, and album.
- Select a track and tap "Request" to submit it.
- See confirmation that my request has been received.
- Be informed if the song has already been requested by someone else, so I can choose a different track.

**UX:** As a member of the audience, I want a clean, simple interface that works well on a mobile phone.

---

## Out of Scope

- QR code generation: the DJ will generate the QR code using an external tool once the deployed URL is known.
- Audience authentication: no login or account is required.
- Audio playback or track previews.
- Artist, album, or playlist search (track search only, initially).
