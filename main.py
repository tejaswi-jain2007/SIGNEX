"""
NTRO SIGINT Master Entry Point.

Usage:
  python main.py gui                  # Launch the PyQt6 Graphical User Interface
  python main.py demo                 # Run full end-to-end synthetic signal demo
  python main.py test                 # Run the complete pytest test suite (147 test cases)
  python main.py process <file.iq>    # Process a specific .iq or .wav signal capture
"""

import sys
import argparse
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def main():
    parser = argparse.ArgumentParser(
        description="NTRO SIGINT Signal Analysis System — Automated IQ/WAV Parameter Extraction & Demodulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python main.py gui
  python main.py demo
  python main.py test
  python main.py process data/demo_capture_qpsk.iq --rate 2000000 --pdf
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="Operational mode")

    # Web subparser
    subparsers.add_parser("web", help="Launch React + Vite Tactical Web Workstation")

    # GUI subparser
    subparsers.add_parser("gui", help="Launch Tactical Desktop GUI (PyQt6)")

    # Demo subparser
    subparsers.add_parser("demo", help="Run end-to-end synthetic demo pipeline")

    # Test subparser
    subparsers.add_parser("test", help="Run full QA verification test suite (pytest)")

    # Process file subparser
    proc_parser = subparsers.add_parser("process", help="Analyze an IQ or WAV file via CLI")
    proc_parser.add_argument("filepath", help="Path to input signal file (.iq, .wav, .raw, .dat)")
    proc_parser.add_argument("--rate", "-r", type=float, default=None, help="Sample rate in Hz (e.g. 2000000)")
    proc_parser.add_argument("--outdir", "-o", default="reports", help="Output directory for reports (default: reports)")
    proc_parser.add_argument("--pdf", action="store_true", default=True, help="Generate classified PDF dossier report")
    proc_parser.add_argument("--no-pdf", dest="pdf", action="store_false", help="Disable PDF dossier generation")

    args = parser.parse_args()

    if args.command == "web":
        from run_web import launch_web
        launch_web()

    elif args.command is None or args.command == "gui":
        print("Launching NTRO SIGINT Tactical Desktop GUI...")
        from ntro_sigint.gui.main_window import launch_gui
        launch_gui()

    elif args.command == "demo":
        from scripts.run_demo import run_demo
        run_demo()

    elif args.command == "test":
        import pytest
        sys.exit(pytest.main(["-v", "tests"]))

    elif args.command == "process":
        from ntro_sigint.core.pipeline import SignalAnalysisPipeline
        pipeline = SignalAnalysisPipeline(model_path="models/amc_resnet18.pt", enforce_airgap=False)
        result = pipeline.process_file(
            filepath=args.filepath,
            output_dir=args.outdir,
            fs_override=args.rate,
            generate_pdf=args.pdf
        )
        print("\n" + "=" * 60)
        print("SIGNAL ANALYSIS RESULT")
        print("=" * 60)
        print(f"File             : {result.input_file}")
        print(f"Sample Rate      : {result.sample_rate / 1e6:.2f} MSps")
        print(f"Modulation       : {result.classification.get('predicted_class', 'Unknown')} ({result.classification.get('confidence', 0.0) * 100:.2f}%)")
        print(f"SNR              : {result.parameters.get('snr_db', 0.0):.2f} dB")
        print(f"Baud Rate        : {result.parameters.get('symbol_rate', 0.0):.2f} Baud")
        print(f"Bandwidth 3dB    : {result.parameters.get('bandwidth_3db', 0.0):.2f} Hz")
        print(f"PAPR             : {result.parameters.get('papr_db', 0.0):.2f} dB")
        print(f"Execution Time   : {result.execution_time_sec:.3f} s")
        print("Generated Files  :")
        for k, v in result.exported_files.items():
            print(f" - {k.upper()}: {v}")
        print("=" * 60)

if __name__ == "__main__":
    main()
