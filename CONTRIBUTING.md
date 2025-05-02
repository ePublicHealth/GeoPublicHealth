# Contributing to GeoPublicHealth

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

The following is a set of guidelines for contributing to the GeoPublicHealth QGIS plugin. These are mostly guidelines, not strict rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

#### Table Of Contents

* [What should I know before I get started?](#what-should-i-know-before-i-get-started)
    * [Code of Conduct](#code-of-conduct)
    * [Technical Context & Design](#technical-context--design)
* [How Can I Contribute?](#how-can-i-contribute)
    * [Reporting Bugs](#reporting-bugs)
    * [Suggesting Enhancements](#suggesting-enhancements)
    * [Your First Code Contribution](#your-first-code-contribution)
    * [Pull Requests](#pull-requests)
* [Styleguides](#styleguides)
    * [Git Commit Messages](#git-commit-messages)
    * [Python Code Styleguide](#python-code-styleguide)
    * [Documentation Styleguide](#documentation-styleguide)
* [Additional Notes](#additional-notes)
    * [Issue and Pull Request Labels](#issue-and-pull-request-labels)

## What should I know before I get started?

### Code of Conduct

This project and everyone participating in it is governed by the [Contributor Covenant Code of Conduct](http://contributor-covenant.org/version/1/4/code_of_conduct.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [manuel@epublichealth.co](mailto:manuel@epublichealth.co).

### Technical Context & Design

GeoPublicHealth is a plugin for QGIS, primarily developed using Python. Understanding the following technical aspects will help you contribute effectively:

* **Core Technologies:** The plugin utilizes the [PyQGIS API](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/) to interact with QGIS data and functionalities, and [PyQt](https://riverbankcomputing.com/software/pyqt/intro) (usually PyQt5 for QGIS 3) for building the user interface.
* **Development Structure:** We strive to follow the [DRY principle](http://c2.com/cgi/wiki?DontRepeatYourself). New analytical methods generally consist of:
    * A User Interface (UI) definition (`.ui` file), created using [Qt Designer](https://doc.qt.io/qtcreator/creator-designer-using.html) (usually bundled with QGIS or PyQt).
    * A Python script generated from the `.ui` file using `pyuic5 -o output_ui.py input.ui` (use `pyuic6` if targeting PyQt6).
    * A separate Python script containing the processing logic (algorithm implementation) using the PyQGIS API and potentially other libraries like `numpy`, `pandas`, `libpysal`, `gdal`, etc.
* **Plugin Structure:** Familiarize yourself with the standard [QGIS Plugin structure](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/plugins/plugin_structure.html).

Think about the required **inputs** and expected **outputs** when designing or implementing a new method.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for GeoPublicHealth. Following these guidelines helps maintainers and the community understand your report :pencil:, reproduce the behavior :computer: :computer:, and find related reports :mag_right:.

#### Before Submitting A Bug Report

* **Perform a [cursory search](https://github.com/ePublicHealth/GeoPublicHealth/issues)** to see if the problem has already been reported. If it has, add a comment to the existing issue instead of opening a new one.

#### How Do I Submit A (Good) Bug Report?

Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/). Create an issue on this repository and provide the following information:

* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as much detail as possible.
* **Provide specific examples to demonstrate the steps**. Include links to files, sample data, or copy/pasteable snippets (using [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines)).
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why.**
* **Include screenshots and animated GIFs** which show you following the described steps and clearly demonstrate the problem. You can use tools like [LiceCap](http://www.cockos.com/licecap/) (macOS/Windows), [Peek](https://github.com/phw/peek) (Linux), or others.
* **If GeoPublicHealth or QGIS crashed**, include relevant parts of the crash report or log messages from the QGIS Log Messages Panel (View -> Panels -> Log Messages). Paste logs in a [code block](https://help.github.com/articles/markdown-basics/#multiple-lines), attach as a file, or link to a [Gist](https://gist.github.com/).
* **If the problem wasn't triggered by a specific action**, describe what you were doing before the problem happened.

Provide more context by answering these questions:

* Can you reliably reproduce the problem?
* Did the problem start happening recently (e.g., after updating QGIS or the plugin)?
* Can you reproduce the problem in an older version?
* Does the problem happen with specific files, projects, data types, or only under certain conditions (e.g., large files, specific projections)?

Include details about your configuration and environment:

* Which version of QGIS are you using (e.g., `QGIS 3.42.2-Münster`)?
* What's the name and version of the OS you're using (e.g., `Windows 11`, `macOS Sonoma 14.4`, `Ubuntu 22.04`)?
* Which version of the GeoPublicHealth plugin are you using?

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for GeoPublicHealth, including new features or improvements to existing functionality.

#### Before Submitting An Enhancement Suggestion

* **Check existing QGIS functionality and other plugins:** Explore the [QGIS plugin repository](https://plugins.qgis.org/) and core QGIS features. What you need might already exist elsewhere.
* **Perform a [cursory search](https://github.com/ePublicHealth/GeoPublicHealth/issues)** to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.

#### How Do I Submit A (Good) Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://guides.github.com/features/issues/). Create an issue on this repository, ideally applying the `enhancement` label, and provide the following information:

* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a step-by-step description of the suggested enhancement** in as much detail as possible.
* **Provide specific examples** to demonstrate its use. Include mock-ups or snippets if helpful (use [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines)).
* **Describe the current behavior (if applicable)** and **explain which behavior you would expect to see instead** and why the enhancement improves it.
* **Include screenshots and animated GIFs** if they help illustrate the proposed feature or the workflow it improves.
* **Explain why this enhancement would be useful** to GeoPublicHealth users, particularly in the context of epidemiology and public health GIS.
* **Mention any other GIS or statistical software** where similar functionality exists, if known.
* **Specify the QGIS and OS versions** you are using.

#### Template For Submitting Enhancement Suggestions (Optional)

```markdown
**[Short description of suggestion]**

**Description of the Enhancement**

[Provide a detailed description of the proposed enhancement and the steps involved in using it.]

**Current Behavior (if applicable)**

[Describe the current way of doing things, if relevant.]

**Suggested Behavior**

[Describe the behavior with the enhancement implemented.]

**Why is this useful?**

[Explain the benefits for users, especially for public health applications.]

**Examples / Use Cases**

[Provide specific examples or scenarios where this would be applied.]

**References (Optional)**

[List any other software or documentation where this feature exists.]

**Screenshots / Mock-ups (Optional)**

[Include images or links here.]

---
**Environment:**
* **QGIS Version:** [Enter QGIS version here]
* **GeoPublicHealth Version:** [Enter plugin version here, if applicable]
* **OS:** [Enter OS name and version here]