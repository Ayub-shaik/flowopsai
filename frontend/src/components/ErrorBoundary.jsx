import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(p){ super(p); this.state = { hasError:false, error:null }; }
  static getDerivedStateFromError(error){ return { hasError:true, error }; }
  componentDidCatch(error, info){ console.error("UI crash:", error, info); }
  render(){
    if (this.state.hasError) {
      return <div className="p-4 text-red-300">
        <div className="text-lg font-bold">UI crashed</div>
        <pre className="text-sm whitespace-pre-wrap">{String(this.state.error)}</pre>
      </div>;
    }
    return this.props.children;
  }
}
