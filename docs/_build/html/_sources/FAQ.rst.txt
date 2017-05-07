.. faq

FAQ
====

Q: 如何获取文档？
^^^^^^^^^^^^^^

A： 安装sphinx然后切入docs目录运行make html即可在./_build/html/index.html中找到html文档，
其他格式见 `sphinx文档 <http://zh-sphinx-doc.readthedocs.io/en/latest/contents.html>`_

.. code-block:: shell
    $ pip install sphinx
    $ cd <resp myserver>/docs
    $ make html
    $ open ./_build/html/index.html
