from metaflow import FlowSpec, step, environment
import os

pod_env_vars = {'AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID'), 'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY')}

class ForeachFlow(FlowSpec):

    @environment(vars=pod_env_vars)
    @step
    def start(self):
        self.titles = ['Stranger Things',
                       'House of Cards',
                       'Narcos']
        self.next(self.a, foreach='titles')
    
    @environment(vars=pod_env_vars)
    @step
    def a(self):
        self.title = '%s processed' % self.input
        self.next(self.join)

    @environment(vars=pod_env_vars)
    @step
    def join(self, inputs):
        self.results = [input.title for input in inputs]
        self.next(self.end)

    @environment(vars=pod_env_vars)
    @step
    def end(self):
        print('\n'.join(self.results))

if __name__ == '__main__':
    ForeachFlow()