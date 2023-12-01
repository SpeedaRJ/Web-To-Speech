from argparse import ArgumentParser, BooleanOptionalAction
from os import remove
from shutil import move

from core.audio_player import AudioPlayer
from core.scrapper import TextScrapper
from core.summarization import TextSummarizer
from core.text_to_pdf import PDFWriter
from core.text_to_speech import VoiceSynthesis

if __name__ == "__main__":
    parser = ArgumentParser(
        description='Parse a website and output its summarization')

    parser.add_argument('-u', '--url', type=str,
                        help='The URL you want to parse', required=True)
    parser.add_argument('-i', '--max_length', type=int,
                        help='The maximum length of the summarization [default max(2500, len(text)//2)]', default=2500)
    parser.add_argument('-j', '--min_length', type=int,
                        help='The maximum length of the summarization [default max(250, len(text)//10)]', default=250)
    parser.add_argument('-p', '--pdf', type=bool,
                        help='Whether to output a PDF file', default=True, action=BooleanOptionalAction)
    parser.add_argument('-P', '--pdf_path', type=str,
                        help='Directory to store the generated pdf', default='')
    parser.add_argument('-s', '--sound', type=bool,
                        help='Whether to auto play the generated summarization', default=True, action=BooleanOptionalAction)
    parser.add_argument('-a', '--audio', type=bool,
                        help='Whether to save the generated audio file', default=True, action=BooleanOptionalAction)
    parser.add_argument('-A', '--audio_path', type=str,
                        help='Directory to store the generated audio file', default='')

    args = parser.parse_args()

    if not args.pdf and not args.sound and not args.audio:
        print("Nothing to do. Exiting...")
        exit(1)

    try:
        steps = 1
        max_steps = 2 + args.pdf + args.sound + args.audio

        pdf_writer = PDFWriter()

        scrapper = TextScrapper()
        print(
            f"[{steps}/{max_steps}] SCRAPPER: FireFox driver initialized. Beginning text extraction...")

        url_text = scrapper.get_text(args.url)
        print(
            f"[{steps}/{max_steps}] SCRAPPER: Text extracted and cleaned...")
        steps += 1

        content_length = len(url_text.split())
        output_limits = [0, float('inf')]

        if args.max_length != 2500:
            output_limits[1] = args.max_length
        else:
            output_limits[1] = max(2500, content_length // 2)

        if args.min_length != 250:
            output_limits[0] = args.min_length
        else:
            output_limits[0] = max(250, content_length // 10)

        summarizer = TextSummarizer(output_limits[1], output_limits[0])
        print(f"[{steps}/{max_steps}] SUMMARIZER: Summarization initialized...")

        summary = summarizer.summarize(url_text)
        title = summarizer.generate_title(url_text)
        filename = pdf_writer.create_filename(title)
        print(f"[{steps}/{max_steps}] SUMMARIZER: Summarization completed...")
        steps += 1

        if args.pdf:
            pdf_writer.add_page(title, summary)
            pdf_writer.save(args.pdf_path)
            print(
                f"[{steps}/{max_steps}] PDF WRITER: PDF created with title {filename}...")
            steps += 1

        synthesizer = None
        if args.sound or args.audio:
            synthesizer = VoiceSynthesis(filename)
            print(
                f"[{steps}/{max_steps}] VOICE SYNTHESIZER: Synthesizer initialized...")

            recording_path = synthesizer.generate_speech(summary)
            print(
                f"[{steps}/{max_steps}] VOICE SYNTHESIZER: Voice synthesis completed...")

            move(recording_path, recording_path.replace("/tmp", ""))

            if args.sound:
                player = AudioPlayer(recording_path.replace("/tmp", ""))
                print(
                    f"[{steps}/{max_steps}] VOICE SYNTHESIZER: Playing voice audio...")
                player.play()
                steps += 1

            synthesizer.destroy()

            if not args.audio:
                remove(recording_path.replace("/tmp", ""))
            else:
                print(
                    f"[{steps}/{max_steps}] VOICE SYNTHESIZER: Voice audio saved...")

        scrapper.destroy()
        exit(0)

    except Exception as e:
        print(f'ERROR encountered: {e}')
        synthesizer.destroy()
        scrapper.destroy()
        exit(1)
