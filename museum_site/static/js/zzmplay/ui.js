const filePicker = document.getElementById('fileOpener');

if (!filePicker) {
  throw new Error("No file picker");
}

filePicker.addEventListener("change", function(e) {
  if (filePicker.files.length > 1) {
    throw new Error("too many files");
  }
  if (filePicker.files.length === 0) {
    // Do nothing
    return;
  }
  const file = filePicker.files[0];
  file.text().then(t => loadNewZzm(t))
});

let selectedFile = undefined;

function loadNewZzm(t) {
  selectedFile = parseZzmAsText(t);

  const title = document.getElementById('fileTitle');
  title.innerText = selectedFile.title;

  const select = document.getElementById('songSelector');
  while (select.firstChild) {
    select.removeChild(select.lastChild);
  }

  let i = 0;
  for (const song of selectedFile.songs) {
    const option = document.createElement("option");
    option.value = i.toString();
    option.innerText = song.title;
    select.appendChild(option);
    i++;
  }

  select.value = '0';
}

document.getElementById("playButton").addEventListener("click", () => {
  if (!selectedFile) {
    return;
  }
  const select = document.getElementById('songSelector');
  const value = select.value;
  if (value === "none") {
    // Should never reach this
    return;
  }

  const index = parseInt(value, 10);
  const song = selectedFile.songs[index];
  if (!song) {
    throw new Error("No song?")
  }
  playZzmAudio(song.data);
});

document.getElementById("dumpButton").addEventListener("click", () => {
  if (!selectedFile) {
    return;
  }
  const select = document.getElementById('songSelector');
  const value = select.value;
  if (value === "none") {
    // Should never reach this
    return;
  }

  const index = parseInt(value, 10);
  const song = selectedFile.songs[index];
  if (!song) {
    throw new Error("No song?")
  }

  const sampleRate = (new AudioContext()).sampleRate
  const data = parseSound(song.data, sampleRate);
  const blob = new Blob([data]);
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a')
  a.href = url;
  a.download = `${song.title} - ${sampleRate}.raw`
  a.click()
});
