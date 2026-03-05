export class NavigationController {
    constructor(graphRenderer) {
        this.main = document.getElementById('mainContainer');
        this.graphRenderer = graphRenderer;
    }

    navigateTo(targetId) {
        if (document.getElementById(targetId).classList.contains('is-active')) return;

        this.main.classList.remove('animating');
        this.main.classList.add('folded');

        setTimeout(() => {
            this.main.classList.add('fly-out');
            setTimeout(() => {
                document.querySelectorAll('.page-view').forEach(v => v.classList.remove('is-active'));
                const nextView = document.getElementById(targetId);
                nextView.classList.add('is-active');

                this.main.classList.remove('fly-out');
                this.main.classList.add('fly-in-start');
                void this.main.offsetWidth;
                this.main.classList.add('animating');
                this.main.classList.remove('fly-in-start');

                setTimeout(() => {
                    this.main.classList.remove('folded');
                    if (targetId === 'result-view') {
                        setTimeout(() => this.graphRenderer.init(window.appState.graphData), 300);
                    }
                }, 600);
            }, 500);
        }, 600);
    }
}
