// SongEditor.tsx using TypeScript and CSS Modules (no Tailwind)

"use client";

import { JSX, useEffect, useState } from "react";
import styles from "./SongEditor.module.css";
import { useDebounce } from "use-debounce";

export default function SongEditor(): JSX.Element {
  const [lyrics, setLyrics] = useState<string>("");
  const [title, setTitle] = useState<string>("");
  const [suggestion, setSuggestion] = useState("");

  const [debouncedLyrics] = useDebounce(lyrics, 500);

  // Fetch suggestion when debounced text changes
  const fetchSuggestion = async (text: string) => {
    if (!text.trim()) return;

    const response = await fetch("http://localhost:8000/api/complete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: title, prompt: text }),
    });
    const data = await response.json();
    setSuggestion(data.completion.trimStart());
  };

  useEffect(() => {
    fetchSuggestion(debouncedLyrics);
  }, [debouncedLyrics]);

  const handleKeyDown = async (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Tab" && suggestion) {
      e.preventDefault(); // Prevent focus moving to next element
      const newLyrics = lyrics + suggestion;
      setLyrics(newLyrics);
      // Clear the suggestion after inserting it
      setSuggestion("");
      await fetchSuggestion(newLyrics);
    }
  };

  //   const handleGenerate = async (): Promise<void> => {
  //     setLoading(true);
  //     try {
  //       console.log(JSON.stringify({ title: title, prompt: lyrics }));
  //       const res = await fetch("http://localhost:8000/api/complete", {
  //         method: "POST",
  //         headers: { "Content-Type": "application/json" },
  //         body: JSON.stringify({ title: title, prompt: lyrics }),
  //       });
  //       const data: { completion: string } = await res.json();
  //       setLyrics((prev) => prev + data.completion);
  //     } catch (error) {
  //       console.error("Error generating lyrics:", error);
  //     } finally {
  //       setLoading(false);
  //     }
  //   };

  return (
    <div className={styles.container}>
      <input
        type="text"
        className={styles.input}
        placeholder="Song Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <div className={styles.lyricsWrapper}>
        <div className={styles.ghostText}>
          <span>{lyrics}&nbsp;</span>
          <span className={styles.suggestion}>{suggestion}</span>
        </div>
        <textarea
          className={styles.textarea}
          value={lyrics}
          onChange={(e) => setLyrics(e.target.value)}
          placeholder="Start your song lyrics here..."
          rows={10}
          onKeyDown={handleKeyDown}
        />
      </div>
    </div>
  );
}
