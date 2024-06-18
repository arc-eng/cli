class PrPilotCli < Formula
  include Language::Python::Virtualenv

  desc "CLI for PR Pilot, a text-to-task automation platform for Github."
  homepage "https://www.pr-pilot.ai"
  license "GPL-3.0"

{{ PACKAGE_URL }}

  depends_on "python@3.10"
  depends_on "rust" => :build

{{ RESOURCES }}

  def install
    virtualenv_create(libexec, "python3")
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/pilot", "--help"
  end
end