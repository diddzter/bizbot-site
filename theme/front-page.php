<?php
/**
 * Homepage. Static copy blocks below mirror data/pages_seed.json's "home"
 * entry -- edit both if the copy changes, since the template is what
 * actually renders (the JSON is the migration-time source of truth).
 */
defined( 'ABSPATH' ) || exit;
get_header();
?>

<section class="bb-hero">
	<div class="bb-container">
		<h1><?php esc_html_e( 'Welcome to BizBot', 'bizbot' ); ?></h1>
		<p><?php esc_html_e( 'Your comprehensive directory for the best business admin tools for your tech company', 'bizbot' ); ?></p>
		<a class="bb-btn" href="#tool-directory"><?php esc_html_e( 'Explore Now', 'bizbot' ); ?></a>
		<p style="margin-top:14px;color:var(--bb-muted);font-size:0.9rem;">
			<?php esc_html_e( 'Find the best tools to streamline your business operations', 'bizbot' ); ?>
		</p>
	</div>
</section>

<section id="tool-directory" class="bb-section">
	<div class="bb-container">
		<h2><?php esc_html_e( 'One-stop directory for the best admin tools for companies.', 'bizbot' ); ?></h2>

		<div class="bb-category-filters">
			<?php
			$categories = get_terms( array( 'taxonomy' => 'tool_category', 'hide_empty' => true ) );
			if ( ! is_wp_error( $categories ) ) {
				foreach ( $categories as $cat ) {
					printf(
						'<a href="%s">%s</a>',
						esc_url( get_term_link( $cat ) ),
						esc_html( $cat->name )
					);
				}
			}
			?>
		</div>

		<div class="bb-tool-grid">
			<?php
			$tools = new WP_Query(
				array(
					'post_type'      => 'tool',
					'posts_per_page' => 8,
					'orderby'        => 'title',
					'order'          => 'ASC',
				)
			);
			while ( $tools->have_posts() ) :
				$tools->the_post();
				$logo   = get_field( 'logo_url' );
				$link   = get_field( 'outbound_url' );
				$cta    = get_field( 'cta_label' ) ?: __( 'Get it', 'bizbot' );
				$cats   = get_the_terms( get_the_ID(), 'tool_category' );
				?>
				<div class="bb-tool-card">
					<?php if ( $logo ) : ?>
						<img class="bb-tool-logo" src="<?php echo esc_url( $logo ); ?>" alt="<?php the_title_attribute(); ?>">
					<?php endif; ?>
					<h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
					<p><?php echo esc_html( wp_trim_words( get_the_excerpt(), 22 ) ); ?></p>
					<?php if ( $cats && ! is_wp_error( $cats ) ) : ?>
						<div class="bb-category-tags">
							<?php foreach ( $cats as $cat ) : ?>
								<span><?php echo esc_html( $cat->name ); ?></span>
							<?php endforeach; ?>
						</div>
					<?php endif; ?>
					<?php if ( $link ) : ?>
						<a class="bb-btn bb-btn-outline" href="<?php echo esc_url( $link ); ?>" rel="nofollow sponsored noopener" target="_blank"><?php echo esc_html( $cta ); ?></a>
					<?php endif; ?>
				</div>
			<?php endwhile; wp_reset_postdata(); ?>
		</div>

		<p style="text-align:center;">
			<a class="bb-btn bb-btn-outline" href="<?php echo esc_url( home_url( '/tools/' ) ); ?>"><?php esc_html_e( 'Show all', 'bizbot' ); ?></a>
		</p>
	</div>
</section>

<section class="bb-section bb-section--soft">
	<div class="bb-container">
		<h2><?php esc_html_e( 'Why Choose Our Directory? Find the Best Admin Tools for Your Business', 'bizbot' ); ?></h2>
		<p class="bb-section-lead">
			<?php esc_html_e( 'We have carefully curated a comprehensive list of the best admin tools for companies, saving you valuable time and effort in finding the right tools to streamline your business operations and boost productivity.', 'bizbot' ); ?>
		</p>
	</div>
</section>

<section id="about-us" class="bb-section">
	<div class="bb-container">
		<h2><?php esc_html_e( 'About Us - The Most Important Things to Know', 'bizbot' ); ?></h2>
		<p class="bb-section-lead">
			<?php esc_html_e( 'Welcome to BizBot, your comprehensive directory for the best business admin tools. We are a team of dedicated professionals committed to providing you with the best admin tools for your business. Our platform is designed to streamline your business operations by offering a one-stop directory for all your admin tool needs. Stay updated with the latest tools and trends, and even suggest a tool for review. Ready to streamline your business? Start exploring our directory now!', 'bizbot' ); ?>
		</p>
	</div>
</section>

<section class="bb-section bb-section--soft">
	<div class="bb-container">
		<h2><?php esc_html_e( 'From the blog', 'bizbot' ); ?></h2>
		<div class="bb-post-grid">
			<?php
			$latest = new WP_Query( array( 'post_type' => 'post', 'posts_per_page' => 4 ) );
			while ( $latest->have_posts() ) :
				$latest->the_post();
				?>
				<a class="bb-post-card" href="<?php the_permalink(); ?>">
					<?php if ( has_post_thumbnail() ) { the_post_thumbnail( 'medium' ); } ?>
					<div class="bb-post-card-body">
						<h3 style="font-size:1rem;margin:0;"><?php the_title(); ?></h3>
					</div>
				</a>
			<?php endwhile; wp_reset_postdata(); ?>
		</div>
	</div>
</section>

<section id="submit-tool" class="bb-section">
	<div class="bb-container">
		<h2 style="text-align:center;"><?php esc_html_e( 'Have a tool to suggest?', 'bizbot' ); ?></h2>
		<p class="bb-section-lead" style="text-align:center;margin:0 auto 24px;">
			<?php esc_html_e( 'Submit your tool for review and get featured in our directory. We value your input and strive to provide the most comprehensive directory possible.', 'bizbot' ); ?>
		</p>
		<?php bizbot_render_form( 'bizbot_tool_submission_shortcode', __( 'Tool submission', 'bizbot' ) ); ?>
	</div>
</section>

<section class="bb-section bb-section--soft">
	<div class="bb-container">
		<h2 style="text-align:center;"><?php esc_html_e( 'Meet Our Team', 'bizbot' ); ?></h2>
		<p class="bb-section-lead" style="text-align:center;margin:0 auto 32px;">
			<?php esc_html_e( 'We are a team of dedicated professionals committed to providing you with the best admin tools for your business.', 'bizbot' ); ?>
		</p>
		<div class="bb-team-grid">
			<div class="bb-team-card">
				<h3>John Rush</h3>
				<p class="bb-role">Tech Maker</p>
				<p><?php esc_html_e( 'Serial startup founder. Leading 20+ products.', 'bizbot' ); ?></p>
			</div>
			<div class="bb-team-card">
				<h3>Didrik Martens</h3>
				<p class="bb-role">Business Maker</p>
				<p>
					<?php
					printf(
						/* translators: %s: link to personal blog */
						esc_html__( 'Serial startup founder looking for help from other entrepreneurs from my projects. Read more about me on my blog %s', 'bizbot' ),
						'<a href="https://www.eggemartens.com/" rel="noopener">eggemartens.com</a>'
					);
					?>
				</p>
			</div>
		</div>
	</div>
</section>

<section class="bb-section">
	<div class="bb-container">
		<h2 style="text-align:center;"><?php esc_html_e( 'Stay Updated', 'bizbot' ); ?></h2>
		<p class="bb-section-lead" style="text-align:center;margin:0 auto 24px;">
			<?php esc_html_e( 'Subscribe to our newsletter for the latest updates and trends in admin tools.', 'bizbot' ); ?>
		</p>
		<?php bizbot_render_form( 'bizbot_newsletter_shortcode', __( 'Newsletter', 'bizbot' ) ); ?>
	</div>
</section>

<?php get_footer(); ?>
