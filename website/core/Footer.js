const React = require('react');

class Footer extends React.Component {

  docUrl(doc, language) {
    const baseUrl = this.props.config.baseUrl;
    const docsUrl = this.props.config.docsUrl;
    const docsPart = `${docsUrl ? `${docsUrl}/` : ''}`;
    const langPart = `${language ? `${language}/` : ''}`;
    return `${baseUrl}${docsPart}${langPart}${doc}`;
  }

  render() {
    return (
      <footer className="nav-footer" id="footer">
      <section className="sitemap">
      <a href={this.props.config.baseUrl} className="nav-home">
      {this.props.config.footerIcon && (
          <img
        src={this.props.config.baseUrl + this.props.config.footerIcon}
        alt={this.props.config.title}
    />
  )}
  </a>
    <div>
    <h5>Docs</h5>
    <a href={this.docUrl('getting-started.html')}>Getting Started</a>
    </div>
    </section>

    <section className="copyright">{this.props.config.copyright}</section>
      </footer>
  );
  }
}

module.exports = Footer;
