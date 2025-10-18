# Terms of Use

## KVG RGB Controller - Open Source Software

**Version:** 0.1.2  
**Last Updated:** October 18, 2025  
**License:** GNU Affero General Public License v3 (AGPLv3) — see LICENSE file

---

## 1. Acceptance of Terms

By downloading, installing, or using KVG RGB Controller ("the Software"), you agree to be bound by these Terms of Use. If you do not agree to these terms, do not use the Software.

---

## 2. Open Source License

This Software is released under the **GNU Affero General Public License v3 (AGPLv3)**.

### What AGPLv3 means (summary):

• ✅ You are free to use, study, modify, and distribute the Software.
• ✅ If you convey (distribute) the Software or a modified version, you must
	also make the corresponding source code available under the same AGPLv3 license.
• 🔁 **Network use triggers copyleft**: If you run a modified version of this
	program on a server and let other users interact with it over a network,
	you must offer the complete, corresponding source code to those users.
• 📋 You must preserve copyright notices and license texts when distributing.

### Key obligations:

- You must release modified source under AGPLv3 when distributing or
	offering the software as a network service.
- You cannot relicense AGPLv3-covered code under a proprietary license.
- You must make the source available, including build scripts and
	any code required to produce the executable.

Please read the full license in `LICENSE` or at https://www.gnu.org/licenses/agpl-3.0.html

---

## 3. Disclaimer of Warranty

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.**

- No warranty of merchantability or fitness for a particular purpose
- No guarantee that the Software will be error-free or uninterrupted
- No liability for any damages resulting from use or inability to use the Software
- No responsibility for hardware damage, data loss, or system instability

---

## 4. Hardware Compatibility & Safety

### RGB Device Control
- This Software interfaces with RGB devices through OpenRGB
- Users are responsible for ensuring compatibility with their hardware
- The authors are not responsible for any hardware damage

### System Requirements
- Requires OpenRGB to be installed and running
- Requires Python 3.8 or higher
- Windows 10/11 recommended for full features (Settings Manager)
- Linux and macOS supported for core functionality

---

## 5. Third-Party Dependencies

This Software relies on third-party libraries and services:

### Core Dependencies:
- **OpenRGB** - RGB device control (GPL-2.0)
- **Flask** - Web framework (BSD-3-Clause)
- **Python OpenRGB** - Python SDK (GPL-3.0)

### Build Dependencies:
- **PyInstaller** - Windows executable creation
- **setuptools** - Python packaging

**Note:** Each dependency has its own license. See the respective projects for details.

---

## 6. Privacy & Data Collection

### Local Data Only:
- All configuration is stored locally in `~/.kvg_rgb/`
- No telemetry, analytics, or data collection
- No internet connection required (except for OpenRGB server communication)
- No user tracking or personal information gathered

### Stored Data:
- RGB device settings and configurations
- Color presets and recent colors
- Autostart preferences
- Database of device/zone configurations

---

## 7. Modifications & Contributions

### Forking & Modifications:
- You may fork and modify this Software freely
- Modified versions should clearly indicate changes
- Consider contributing improvements back to the main project

### Contributing:
- Contributions via pull requests are welcome
- By contributing, you agree to license your contributions under the MIT License
- See CONTRIBUTING.md (if available) for guidelines

---

## 8. Commercial Use

**Commercial use is explicitly permitted** under the MIT License:
- ✅ Use in commercial products
- ✅ Sell modified versions
- ✅ Include in proprietary software
- ✅ No royalties or fees required

**However:**
- Attribution must be provided
- Original license must be included
- No warranty or liability claims

---

## 9. Support & Maintenance

### No Guaranteed Support:
- This is open source software provided "as-is"
- No obligation to provide support, updates, or bug fixes
- Community support available via GitHub Issues

### Updates:
- Software may be updated at any time
- No guarantee of backward compatibility
- Users should backup configurations before updating

---

## 10. Security

### User Responsibility:
- Users are responsible for securing their systems
- Review source code before running if concerned
- Use at your own risk

### Reporting Vulnerabilities:
- Security issues should be reported via GitHub Issues
- No bug bounty program exists

---

## 11. Termination

- These terms remain in effect until terminated
- You may stop using the Software at any time
- Uninstalling removes the Software but preserves user data in `~/.kvg_rgb/`

---

## 12. Jurisdiction & Dispute Resolution

- This Software is distributed internationally
- Disputes governed by applicable local laws
- No mandatory arbitration

---

## 13. Changes to Terms

- These terms may be updated in future releases
- Continued use after updates constitutes acceptance
- Check GitHub repository for latest terms

---

## 14. Contact & Attribution

**Project Repository:** https://github.com/gerp93/KVG_RGB  
**License:** MIT License  
**Author:** gerp93

**Dependencies:**
- OpenRGB Project: https://openrgb.org
- Python OpenRGB: https://github.com/jath03/openrgb-python

---

## 15. Acknowledgments

This Software would not be possible without:
- The OpenRGB project and community
- Python and the Flask framework
- All contributors to the project
- The RGB hardware community

---

## Summary

**In Plain English:**

This is free, open source software. You can use it however you want, modify it, and even sell it. Just include the license file and don't blame us if something goes wrong. We make no promises about it working perfectly, but we've done our best to make it useful and reliable.

**Questions?** Open an issue on GitHub!

---

**Last Updated:** October 18, 2025  
**Version:** 0.1.2
