# SPDX-License-Identifier: LGPL-3.0-or-later

"""
This is the graphs subpackage for the Maeser package.

This package contains **Retrieval-Augmented Generation (RAG) graphs** that affect the workflow and behavior of the chatbot.
Maeser's RAG graphs and their functionality are as follows:

:simple_rag: Accepts only one vector store, forcing the chatbot to stick to one topic per conversation.
:pipeline_rag: Accepts multiple vector stores, allowing the chatbot to dynamically choose the most relevant vector store when answering a user's question. However, only one vector store can be accessed per response.
:universal_rag: Accepts multiple vector stores, like **pipeline_rag**, but also pulls from as many vector stores as needed (or none at all) per response.
"""

from maeser._utils.pkg_utils import autoimport_all
import sys

__all__ = autoimport_all(sys.modules[__name__], include_packages=True)
